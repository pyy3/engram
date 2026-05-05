class Engram < Formula
  desc "Persistent 5-layer memory system for Claude Code and AI coding agents"
  homepage "https://github.com/grynn-in/engram"
  url "https://github.com/grynn-in/engram/archive/refs/tags/v0.6.0.tar.gz"
  sha256 "PLACEHOLDER"
  license "MIT"

  depends_on "python@3.11"

  def install
    # Install scripts to libexec
    libexec.install Dir["bin/*"]
    libexec.install Dir["lib/*"]

    # Install templates
    (share/"engram/templates").install Dir["templates/*"]

    # Create wrapper that sets up environment
    (bin/"engram").write <<~EOS
      #!/bin/bash
      export ENGRAM_HOME="${ENGRAM_HOME:-#{var}/engram}"
      exec "#{libexec}/engram" "$@"
    EOS

    # Install completions
    bash_completion.install "completions/engram.bash" => "engram"
    zsh_completion.install "completions/engram.zsh" => "_engram"
  end

  def post_install
    (var/"engram").mkpath
  end

  test do
    system "#{bin}/engram", "version"
  end
end
