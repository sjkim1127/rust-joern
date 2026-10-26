struct VF { int operator()(int x) volatile { return x; } };
struct H { volatile VF call; };
int field_volatile(H& h) { return h.call(1); }
