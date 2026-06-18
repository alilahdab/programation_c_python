

import sympy as sp

# ----------------------------------------------------------
# (a) Définition symbolique de f(x, y) et calcul du gradient
# ----------------------------------------------------------
x, y = sp.symbols('x y', real=True)

f = x**3 + y**3 - 3*x*y
print("Fonction f(x, y) =", f)

df_dx = sp.diff(f, x)
df_dy = sp.diff(f, y)
gradient = sp.Matrix([df_dx, df_dy])

print("\n--- (a) Gradient de f ---")
print("df/dx =", df_dx)
print("df/dy =", df_dy)
print("Gradient ∇f(x, y) =")
sp.pprint(gradient)

# ----------------------------------------------------------
# (b) Matrice jacobienne du gradient
# ----------------------------------------------------------
jacobienne = gradient.jacobian([x, y])

print("\n--- (b) Matrice jacobienne du gradient ---")
sp.pprint(jacobienne)

# ----------------------------------------------------------
# (c) Matrice hessienne
# ----------------------------------------------------------
hessienne = sp.hessian(f, (x, y))

print("\n--- (c) Matrice hessienne ---")
sp.pprint(hessienne)

# (On remarque que la jacobienne du gradient = la hessienne de f)

# ----------------------------------------------------------
# (d) Points critiques : résolution de ∇f(x, y) = (0, 0)
# ----------------------------------------------------------
points_critiques = sp.solve([df_dx, df_dy], [x, y], dict=True)

print("\n--- (d) Points critiques ---")
for p in points_critiques:
    print(p)

# ----------------------------------------------------------
# (e) Nature de chaque point critique via la hessienne
# ----------------------------------------------------------
print("\n--- (e) Nature des points critiques ---")
for p in points_critiques:
    xc, yc = p[x], p[y]
    H_eval = hessienne.subs({x: xc, y: yc})
    det_H = H_eval.det()
    H11 = H_eval[0, 0]

    print(f"\nPoint critique : (x, y) = ({xc}, {yc})")
    print("Hessienne en ce point :")
    sp.pprint(H_eval)
    print("Déterminant de la hessienne :", det_H)

    if det_H > 0 and H11 > 0:
        nature = "Minimum local"
    elif det_H > 0 and H11 < 0:
        nature = "Maximum local"
    elif det_H < 0:
        nature = "Point selle (col)"
    else:
        nature = "Cas indéterminé (étude supplémentaire nécessaire)"

    print("Conclusion :", nature)