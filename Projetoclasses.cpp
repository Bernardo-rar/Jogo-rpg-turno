
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

class arma{
    public://simplificar por enquanto.
        int dano;
        char Tipo;
    int UparArma(arma a){
        a.dano+=a.dano;
    }

    int DardanoFisico(int str,int dex){// ver comno usa a rand.
        rand();
    }
};


class personagem{

    //unificar os mods de hp,stamina contara cm hit dice como no exemplo do homebrew.
    
    
    public:
        int lvl,str,dex,con,imt,wis,cha,stamina,gold,dadoinicialHP,mana,HPregen,MPregen;
        arma inicial;

    //hp regen valer para stamina?

    int Calculabonus(int Atributo){
        int Acumulador=0;
        if(Atributo>=4){
			Acumulador=(((Atributo-4)/2)+1)*2; // dessa forma 18,22,26 terao buffs
            
            if(Atributo>=10){
                Acumulador+=(((Atributo-10)/2)+1)*2; //hiper especialização valera a pena 
            }
		}
        return Acumulador; 
    }
    
    int CalculaHP(){
        int tough,modHP=0;
		tough=Calculabonus(str);
        modHP=Calculabonus(con);
    //ver teste no diretrizes, assim como no 2e, vida dobrada lvl 1 
		return (dadoinicialHP+con+tough)*(lvl+1)*(10+modHP);    
    }


   int CalculaMana(){
        int mind=Calculabonus(wis)+Calculabonus(imt)+Calculabonus(cha);
        
        return (wis+cha+imt+mind)*(lvl+1)*5; 

    }
    
    int CalculaArmor(){//ver como vao ficar os sclaes
        int armor=Calculabonus(str)+Calculabonus(dex)+Calculabonus(con);
        return str+con+dex+armor/2;
    }
     
     int CalculaMR(){
        int armor=Calculabonus(wis)+Calculabonus(imt)+Calculabonus(con);
        return wis+imt+con+armor/2;
    }

    int Resistdebuffmagico(){// sistema de darkest dungeon de %.

    }

    personagem(int nvl,int f,int d,int c,int i,int w,int ch,int ddIHP){
        lvl=nvl;
        str=f;
        dex=d;
        con=c;
        imt=i;
        wis=w;
        cha=ch;
        dadoinicialHP=ddIHP;

    };
};


class guerreiro:public personagem{
   
};

//calsses darem buffs em % pros atributos.
    //lvl 1

int main(){
    personagem batata(10,10,10,10,10,10,10,10);
    batata.str=14;
    batata.inicial.dano=10;
    batata.CalculaHP();
    printf("hlo word\n");
    printf("teste\n");
    printf("%d",batata.CalculaHP());
}

