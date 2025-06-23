// Minimal AoPS olympiad macros placeholder
// Only a very small subset of the real library is provided.
import graph;

picture grid(int m, int n) {
  picture p;
  for (int i=0; i<=m; ++i) {
    draw(p, (i,0)--(i,n), lightgray);
  }
  for (int j=0; j<=n; ++j) {
    draw(p, (0,j)--(m,j), lightgray);
  }
  return p;
}
