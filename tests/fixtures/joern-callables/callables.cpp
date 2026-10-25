int fn(int); // Caller parameters deliberately shadow this global function.
int tick();
struct Plain { int operator()(int); };
int direct(Plain& fn) { return fn(tick()); }
int grouped(Plain& fn) { return (fn)(tick()); }
int dereferenced(Plain* fn) { return (*fn)(tick()); }
int indexed(Plain* fn, int i) { return fn[i++](tick()); }
int nested(Plain& fn) { return fn(fn(tick())); }
int explicit_call(Plain& fn) { return fn.operator()(tick()); }
namespace demo { struct Callable { int operator()(int); }; }
int namespaced(demo::Callable& fn) { return fn(5); }
struct Overloaded { int operator()(int); int operator()(char*); };
int overloaded_int(Overloaded& fn) { return fn(6); }
int overloaded_pointer(Overloaded& fn, char* text) { return fn(text); }
struct Arity { int operator()(); int operator()(int,int); };
int zero(Arity& fn) { return fn(); }
int two(Arity& fn) { return fn(tick(),tick()); }
struct Virtual { virtual int operator()(int); };
int virtual_call(Virtual& fn) { return fn(7); }
struct Const { int operator()(int) const; };
int const_object(const Const& fn) { return fn(8); }
int const_method(Const& fn) { return fn(9); }
// These two rows deliberately contain unknown types, like decompiler output.
int unresolved_argument(Plain& fn, Unknown value) { return fn(value); }
int unresolved_overload(Overloaded& fn, Unknown value) { return fn(value); }
