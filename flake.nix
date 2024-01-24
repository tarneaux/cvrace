{
  description = "cvrace";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.11";
    nixpkgs-unstable.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs, nixpkgs-unstable, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      pkgs-unstable = nixpkgs-unstable.legacyPackages.${system};
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        nativeBuildInputs = with pkgs; [
          ( let python =
              let
                packageOverrides = self:
                super: {
                  opencv4 = super.opencv4.override {
                    enableGtk2 = true;
                    gtk2 = pkgs.gtk2;
                    enableFfmpeg = true;
                  };
                };
              in
                pkgs.python3.override {inherit packageOverrides; self = python;};
            in
              python.withPackages (ps: with ps; [ numpy opencv4 ]))
          gtk2-x11
          pkg-config
        ];
      };
    };
}
