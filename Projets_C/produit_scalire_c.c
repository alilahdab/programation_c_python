#include <stdio.h>
#include <stdlib.h>
int main()
{
    int t[3], n[3];
    int p = 0;
    int i;

    printf("Entrer les elements du premier tableau :\n");
    for (i = 0; i < 3; i++) {
        printf("t[%d] = ", i);
        scanf("%d", &t[i]);
    }

    printf("Entrer les elements du deuxieme tableau :\n");
    for (i = 0; i < 3; i++) {
        printf("n[%d] = ", i);
        scanf("%d", &n[i]);
    }

    for (i = 0; i < 3; i++) {
        p = p + (t[i] * n[i]);
    }

    printf("Le produit scalaire est : %d\n", p);

    return 0;
}
