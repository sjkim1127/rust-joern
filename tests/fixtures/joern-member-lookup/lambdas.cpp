int plain() { auto f = [](int x) -> int { return x; }; return f(1); }
int grouped() { auto f = ([](int x) -> int { return x; }); return f(1); }
int invoked() { return ([](int x) -> int { return x; })(1); }
struct H {
  int a[([]() { return 2; })()] = {1, 2};
  int b = ([]() { return 3; })();
};
