struct F { int operator()(int x) { return x; } };
struct CF { int operator()(int x) const { return x; } };
using Alias = F;
typedef F Alias2;
using ConstAlias = const CF;
namespace N { using A = F; struct H { A f; }; }
struct H { Alias f; Alias2 g; ConstAlias c; const CF fixed; CF plain; mutable F mut; };
struct B { F f; int method(int x) { return x; } };
struct D : public B {};
struct E : D {};
int alias(H& h) { return h.f(1) + h.g(2); }
int namespace_alias(N::H& h) { return h.f(1); }
int alias_cv(H& h) { return h.c(1); }
int field_cv(H& h) { return h.fixed(1); }
int owner_cv(const H& h) { return h.plain(1); }
int mutable_cv(const H& h) { return h.mut(1); }
int inherited(D& d) { return d.f(1); }
int multilevel(E* e) { return e->f(1); }
int inherited_method(D& d) { return d.method(1); }
int local_alias(Alias& x) { return x(1); }
int local_cv_alias(ConstAlias& x) { return x(1); }
using Chain = Alias;
struct ChainHolder { Chain f; };
int chained_alias(ChainHolder& h) { return h.f(1); }
struct FnDerived : public F {};
int inherited_callable(FnDerived& f) { return f(1); }
struct Hidden : B { CF f; };
int hidden_field(Hidden& h) { return h.f(1); }
namespace M { using A = CF; struct H { A f; }; }
int other_alias(M::H& h) { return h.f(1); }
namespace N { struct Later { A f; }; }
int prior_namespace_alias(N::Later& h) { return h.f(1); }
void local_scope() { using Alias = CF; }
struct AfterLocal { Alias f; };
int after_local(AfterLocal& h) { return h.f(1); }
int tick();
int inherited_effects(D* ds) { return ds[tick()].f(tick()); }
