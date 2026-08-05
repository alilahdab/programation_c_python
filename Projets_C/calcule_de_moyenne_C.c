#include <stdio.h>
#include <stdlib.h>

int main()
{
    int T[10];
  int i,som=0 ;
  float moy;
  int x=0;
   printf("entrer les note des etudiant:\n");
   for (i=0;i<10;i++){
    printf("T[%d]= ",i);
    scanf("%d",&T[i]);
   }
   for (i=0;i<10;i++){
    som=som+T[i];
   }
 moy=som/10.0;
 printf("la moyenne est :%.2f\n",moy);
 for (i=0;i<10;i++){
    if (T[i]>moy)
        printf("les note supp a la moyenne sont : %d\n",T[i]);
 }
 for (i=0;i<10;i++){
         if (T[i]>moy)
          x++;

 }
    printf("le nombre des note supp a la moyenne :%d",x);
    return 0;
}
