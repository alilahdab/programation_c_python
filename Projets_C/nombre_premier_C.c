#include <stdio.h>
#include <stdlib.h>

int main()
{
    int p = 0, i, n;

    printf("Entrez un nombre: ");
    if (scanf("%d", &n) != 1) {
        printf("Erreur de saisie.\n");
        return 1;
    }

    if (n < 2) {
        printf("Le nombre n'est pas premier : %d\n", n);
        return 0;
    }

    for(i = 1; i <= n; i++)
    {
        if(n % i == 0)
        {
            p = p + 1;
        }
    }

    if(p == 2)
    {
        printf("Le nombre est premier : %d\n", n);
    }
    else
    {
        printf("Le nombre n'est pas premier : %d\n", n);
    }

    return 0;
}
