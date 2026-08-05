#include <stdio.h>
#include <stdlib.h>

// Fonctions de calcul
double add(double a, double b) {
    return a + b;
}

double sub(double a, double b) {
    return a - b;
}

double mul(double a, double b) {
    return a * b;
}

double divs(double a, double b) {
    if (b == 0) {
        printf("Erreur : Division par zero impossible !\n");
        return 0.0;}
    return a / b;
}

int main() {
    double a, b;
    char op, choice;

    do {
        printf("\n--- Nouvelle Operation ---\n");
        printf("Entrez le premier nombre : ");
        scanf("%lf", &a);

        printf("Entrez l'operateur (+, -, *, /) : ");
        scanf(" %c", &op);

        printf("Entrez le deuxieme nombre : ");
        scanf("%lf", &b);

        switch (op) {
            case '+':
                printf("Resultat : %.2lf + %.2lf = %.2lf\n", a, b, add(a, b));
                break;
            case '-':
                printf("Resultat : %.2lf - %.2lf = %.2lf\n", a, b, sub(a, b));
                break;
            case '*':
                printf("Resultat : %.2lf * %.2lf = %.2lf\n", a, b, mul(a, b));
                break;
            case '/':
                if (b != 0)
                    printf("Resultat : %.2lf / %.2lf = %.2lf\n", a, b, divs(a, b));
                break;
            default:
                printf("Operateur non valide !\n");
        }

        printf("\nVoulez-vous faire un autre calcul ? (y/n) : ");
        scanf(" %c", &choice);

    } while (choice == 'y' || choice == 'Y');

    printf("\nL3zz sality ! :)\n");

    return 0;
}
