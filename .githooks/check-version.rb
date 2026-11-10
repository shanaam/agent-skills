# Blocks a commit that changes skills/ without raising "version" in
# .claude-plugin/plugin.json. claude.ai and Claude Code use that version to
# decide whether there is anything new, so an unchanged version can leave the
# synced copy stale.
#
# Compares the staged plugin.json with the last pushed commit (the branch's
# upstream, or HEAD when there is none), so one bump covers every commit in a
# push and `git commit --amend` doesn't trip it.
#
# Usage: ruby .githooks/check-version.rb   (from the repo root; the pre-commit
# hook runs it)

require "json"
require "open3"

MANIFEST = ".claude-plugin/plugin.json".freeze

def git(*args)
  out, status = Open3.capture2("git", *args, err: File::NULL)
  status.success? ? out.strip : nil
end

def fail_with(lines)
  warn "check-version: #{lines.shift}"
  lines.each { |line| warn "  #{line}" }
  exit 1
end

def next_patch(version)
  version.sub(/(\d+)(?!.*\d)/) { (Regexp.last_match(1).to_i + 1).to_s }
end

base = git("rev-parse", "--verify", "-q", "@{upstream}")
base_label = git("rev-parse", "--abbrev-ref", "@{upstream}") if base
if base.nil? || base.empty?
  base = git("rev-parse", "--verify", "-q", "HEAD")
  base_label = "HEAD"
end
exit 0 if base.nil? || base.empty? # first commit: nothing to compare with

changed = git("diff", "--cached", "--name-only", "--no-renames", base, "--", "skills/").to_s.split("\n")
exit 0 if changed.empty?

shown = changed.first(5).join(", ") + (changed.size > 5 ? ", and #{changed.size - 5} more" : "")

staged_text = git("show", ":#{MANIFEST}")
fail_with(["skills/ changed, but #{MANIFEST} is missing.", "Changed: #{shown}"]) unless staged_text
begin
  new_version = JSON.parse(staged_text)["version"]
rescue JSON::ParserError => e
  fail_with(["#{MANIFEST} is not valid JSON (#{e.message.lines.first.strip})."])
end
unless new_version.is_a?(String) && Gem::Version.correct?(new_version)
  fail_with(["skills/ changed, but #{MANIFEST} has no valid version (found #{new_version.inspect}).",
             "Add one like \"version\": \"1.0.0\" and stage it."])
end

old_text = git("show", "#{base}:#{MANIFEST}")
old_version = begin
  old_text && JSON.parse(old_text)["version"]
rescue JSON::ParserError
  nil
end
exit 0 unless old_version.is_a?(String) && Gem::Version.correct?(old_version) # first version: nothing to beat

if Gem::Version.new(new_version) <= Gem::Version.new(old_version)
  state = new_version == old_version ? "is still" : "went down to"
  fail_with(["skills/ changed, but the version #{state} #{new_version} (#{base_label} has #{old_version}).",
             "Raise \"version\" in #{MANIFEST}, e.g. to #{next_patch(old_version)}, and stage it.",
             "Changed: #{shown}"])
end
exit 0
