namespace N {
class Callable { public: int operator()(int x) { return x; } };
class Holder { public: Callable field; Callable *pointer; Callable *array; int scalar; int method(int x) { return x; } };
class Nested { public: Holder inner; };
}
int tick();
int direct(N::Holder &a) { return a.field(1); }
int indirect(N::Holder *a) { return a->field(2); }
int nested(N::Nested &a) { return a.inner.field(3); }
int dereferenced(N::Holder &a) { return (*a.pointer)(4); }
int indexed(N::Holder &a) { return a.array[tick()](tick()); }
int owner_index(N::Holder *a) { return a[tick()].field(tick()); }
int field_argument(N::Holder &a) { return a.field(a.scalar); }
int ordinary(N::Holder &a) { return a.method(1); }
