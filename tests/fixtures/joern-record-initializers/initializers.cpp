int seed();
constexpr int bound() { return 2; }
namespace N {
struct Plain { int x; void body() {} };
struct Arrays {
  int a[2];
  int matrix[2][3];
  int data[2] = {1, 2};
};
struct Values {
  int a = 7;
  int b{8};
  int c = seed();
  inline static int s = seed();
};
struct Outer {
  struct Inner { int a[2]; };
  int a[bound()];
};
}
