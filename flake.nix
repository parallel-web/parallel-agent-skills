{
  description = "parallel-agent-skills dev shell";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};

      pnpm = pkgs.writeShellScriptBin "pnpm" ''
        exec corepack pnpm "$@"
      '';
    in {
      devShells.default = pkgs.mkShell {
        packages = [pkgs.nodejs_25 pnpm pkgs.pre-commit];
      };
    });
}
