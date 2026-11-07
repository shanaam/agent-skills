# Checks every <folder>/SKILL.md under a directory against the skill rules
# claude.ai's marketplace sync enforces. Claude Code's own validator
# (`claude plugin validate`, even with --strict) does not catch these, and one
# failing skill fails the sync for the whole plugin.
#
# Usage: ruby .githooks/check-skills.rb [dir]   (dir defaults to .)
# The pre-commit hook runs it on the staged copy of the repo.

require "yaml"

MAX_NAME = 64
MAX_DESCRIPTION = 1024
RESERVED_WORDS = %w[claude anthropic].freeze

def problems_for(path, folder)
  text = File.read(path, encoding: "UTF-8")
  match = text.match(/\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\z)/m)
  return ["no frontmatter: the file must start with a --- block"] unless match

  begin
    frontmatter = YAML.safe_load(match[1])
  rescue Psych::Exception => e
    return ["frontmatter is not valid YAML (#{e.message}). " \
            "Quote values that contain \": \", e.g. description: '...'"]
  end
  return ["frontmatter is not a key: value mapping"] unless frontmatter.is_a?(Hash)

  problems = []
  name = frontmatter["name"]
  description = frontmatter["description"]

  if !name.is_a?(String) || name.empty?
    problems << "name is missing or not a string"
  else
    problems << "name '#{name}' must match its folder '#{folder}'" if name != folder
    unless name.match?(/\A[a-z0-9-]{1,#{MAX_NAME}}\z/)
      problems << "name must be 1-#{MAX_NAME} lowercase letters, digits, or hyphens"
    end
    RESERVED_WORDS.each do |word|
      problems << "name contains the reserved word '#{word}'" if name.include?(word)
    end
  end

  if !description.is_a?(String) || description.strip.empty?
    problems << "description is missing or not a string"
  else
    if description.length > MAX_DESCRIPTION
      problems << "description is #{description.length} characters (max #{MAX_DESCRIPTION})"
    end
    if description.match?(/[<>]/)
      problems << "description contains < or > (no XML-style tags; write {app} instead of <app>)"
    end
  end
  problems
end

root = ARGV[0] || "."
skills = Dir.glob(File.join(root, "*", "SKILL.md")).sort
if skills.empty?
  puts "check-skills: no <folder>/SKILL.md files found under #{root}"
  exit 0
end

failures = skills.map do |path|
  folder = File.basename(File.dirname(path))
  problems = problems_for(path, folder)
  [folder, problems] unless problems.empty?
end.compact

if failures.empty?
  puts "check-skills: all #{skills.size} skills pass claude.ai's skill rules"
  exit 0
end

warn "check-skills: #{failures.size} of #{skills.size} skills would fail claude.ai's marketplace sync:"
failures.each do |folder, problems|
  problems.each { |problem| warn "  #{folder}/SKILL.md: #{problem}" }
end
exit 1
