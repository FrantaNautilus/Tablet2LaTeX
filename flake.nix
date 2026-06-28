{
  description = "Development environment for Tablet2LaTeX GTK4 conversion";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # 1. DEFINE PYTHON ENV: Create a specific interpreter with libraries baked in
        pythonEnv = pkgs.python312.withPackages (ps: with ps; [
          pillow
          openai
          pyperclip
          numpy
          pycairo
          pygobject3 # This provides the 'gi' module
          setuptools
          wheel
        ]);

        # Python packages for testing and linting
        pythonTestEnv = pkgs.python312.withPackages (ps: with ps; [
          pytest
          pytest-cov
          pillow
          openai
          pyperclip
          numpy
          pycairo
          pygobject3
        ]);

        # GTK4 and libadwaita runtime libraries
        gtkLibs = with pkgs; [
          gtk4
          libadwaita
          gobject-introspection
          cairo
        ];

        devDeps = with pkgs; [
          ruff
          black
          isort
          mypy
          flatpak-builder
          appstream
          wl-clipboard
        ];

        # Linting script
        lintScript = pkgs.writeShellScriptBin "tablet2latex-lint" ''
          echo "🔍 Running ruff linter..."
          ${pkgs.ruff}/bin/ruff check src/tablet2latex/ "$@"
        '';

        # Formatting script
        formatScript = pkgs.writeShellScriptBin "tablet2latex-format" ''
          echo "🎨 Running black formatter..."
          ${pkgs.black}/bin/black src/tablet2latex/ "$@"
        '';

        # Type checking script
        typecheckScript = pkgs.writeShellScriptBin "tablet2latex-typecheck" ''
          echo "🔎 Running mypy type checker..."
          ${pkgs.mypy}/bin/mypy src/tablet2latex/ "$@"
        '';

        # Testing script
        testScript = pkgs.writeShellScriptBin "tablet2latex-test" ''
          echo "🧪 Running pytest..."
          export PYTHONPATH="$PWD/src:$PYTHONPATH"
          # Move tablet2latex.py temporarily to avoid import conflicts
          mv "$PWD/tablet2latex.py" "$PWD/tablet2latex.py.bak" 2>/dev/null || true
          ${pythonTestEnv}/bin/pytest "$@" -v "$PWD/tests"
          TEST_EXIT=$?
          # Restore tablet2latex.py
          mv "$PWD/tablet2latex.py.bak" "$PWD/tablet2latex.py" 2>/dev/null || true
          exit $TEST_EXIT
        '';

        # All checks script
        checkScript = pkgs.writeShellScriptBin "tablet2latex-check" ''
          echo "🔍 Running all checks..."
          echo ""
          echo "=== Ruff Linter ==="
          ${pkgs.ruff}/bin/ruff check src/tablet2latex/ || exit 1
          echo ""
          echo "=== Black Formatter Check ==="
          ${pkgs.black}/bin/black --check src/tablet2latex/ || exit 1
          echo ""
          echo "=== Mypy Type Checker ==="
          ${pkgs.mypy}/bin/mypy src/tablet2latex/ || exit 1
          echo ""
          if [ -d "tests" ]; then
            echo "=== Pytest ==="
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            # Move tablet2latex.py temporarily to avoid import conflicts
            mv "$PWD/tablet2latex.py" "$PWD/tablet2latex.py.bak" 2>/dev/null || true
            ${pythonTestEnv}/bin/pytest -v "$PWD/tests"
            TEST_EXIT=$?
            # Restore tablet2latex.py
            mv "$PWD/tablet2latex.py.bak" "$PWD/tablet2latex.py" 2>/dev/null || true
            if [ $TEST_EXIT -ne 0 ]; then exit 1; fi
          else
            echo "⚠️  No tests directory found, skipping pytest"
          fi
          echo ""
          echo "✅ All checks passed!"
        '';

        # Run script
        runScript = pkgs.writeShellScriptBin "tablet2latex-run" ''
          export PYTHONPATH="$PWD/src:$PYTHONPATH"
          ${pythonEnv}/bin/python tablet2latex.py "$@"
        '';

      in {
        devShells.default = pkgs.mkShell {
          # 2. ADD HOOKS: wrapGAppsHook4 automatically sets GI_TYPELIB_PATH
          nativeBuildInputs = with pkgs; [
            pkg-config
            wrapGAppsHook4
            gobject-introspection
          ];

          # 3. USE CUSTOM PYTHON: Add the env we defined above
          buildInputs = [ pythonEnv ] ++ gtkLibs ++ devDeps ++ [
            lintScript
            formatScript
            typecheckScript
            testScript
            checkScript
            runScript
          ];

          shellHook = ''
            echo "📋 Tablet2LaTeX GTK4 Development Environment"
            echo "============================================"
            echo "Verifying 'gi' module..."
            python -c "import gi; print(f'✅ PyGObject found: {gi.__file__}')" || echo "❌ PyGObject NOT found"
            echo ""
            echo "Available commands:"
            echo "  tablet2latex-run       - Run the application"
            echo "  tablet2latex-lint      - Run ruff linter"
            echo "  tablet2latex-format    - Run black formatter"
            echo "  tablet2latex-typecheck - Run mypy type checker"
            echo "  tablet2latex-test      - Run pytest"
            echo "  tablet2latex-check     - Run all checks"
            echo ""
            echo "Or use nix run:"
            echo "  nix run .#run          - Run the application"
            echo "  nix run .#lint         - Run linter"
            echo "  nix run .#format       - Run formatter"
            echo "  nix run .#typecheck    - Run type checker"
            echo "  nix run .#test         - Run tests"
            echo "  nix run .#check        - Run all checks"
            echo ""
          '';
        };

        # Package for installation
        packages.default = pkgs.python312Packages.buildPythonPackage {
          pname = "tablet2latex";
          version = "1.0.0";
          src = ./.;
          format = "other";
          
          # Native inputs are needed at build time (hooks)
          nativeBuildInputs = [ pkgs.wrapGAppsHook4 pkgs.gobject-introspection ];
          
          # Propagated inputs are runtime dependencies
          propagatedBuildInputs = [ pythonEnv ] ++ gtkLibs;

          installPhase = ''
            mkdir -p $out/bin
            cp tablet2latex.py $out/bin/tablet2latex
            chmod +x $out/bin/tablet2latex
          '';
        };

        # Apps for nix run commands
        apps = {
          default = {
            type = "app";
            program = "${runScript}/bin/tablet2latex-run";
          };
          run = {
            type = "app";
            program = "${runScript}/bin/tablet2latex-run";
          };
          lint = {
            type = "app";
            program = "${lintScript}/bin/tablet2latex-lint";
          };
          format = {
            type = "app";
            program = "${formatScript}/bin/tablet2latex-format";
          };
          typecheck = {
            type = "app";
            program = "${typecheckScript}/bin/tablet2latex-typecheck";
          };
          test = {
            type = "app";
            program = "${testScript}/bin/tablet2latex-test";
          };
          check = {
            type = "app";
            program = "${checkScript}/bin/tablet2latex-check";
          };
        };
      });
}
