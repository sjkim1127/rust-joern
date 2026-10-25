class Foo {
  auto first = [] (int x) -> int { return x + 1; };
  void body() { auto middle = [] (int x) -> int { return x + 2; }; }
  auto last = [] (int x) -> int { return x + 3; };
};
