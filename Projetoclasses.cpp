
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
class armardura{
    public:
        int vida,mana,DefesaF,DefesaM;

    armardura(){
        vida=10;
        mana=10;
        DefesaF=10;
        DefesaM=10;
    }


};

class acessorio{
    int vida,mana,stauts;
};

class itensconsumiveis{
    int vida,mana,buff;
    //ver como vai fazer
};

class inventario{
    itensconsumiveis itens[20];
    armardura armor[20];
    arma weapon[20];
};

class skill{
    public:
        int dano,cura,efeito;
};
class personagem{

    //unificar os mods de hp,stamina contara cm hit dice como no exemplo do homebrew.
    
    
    public:
        int lvl,str,dex,con,imt,wis,cha,stamina,gold,dadoinicialHP,HP,mana,HPregen,MPregen;
        arma espadaequipada;
        armardura armaduraequipada;

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
		return (dadoinicialHP+con+tough)*(lvl+1)*(10+modHP)+armaduraequipada.vida;    
    }


   int CalculaMana(){
        int mind=Calculabonus(wis)+Calculabonus(imt)+Calculabonus(cha);
        
        return (wis+cha+imt+mind)*(lvl+1)*5+armaduraequipada.mana; 

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

    personagem(){
        lvl=1;
        str=10;
        dex=10;
        con=10;
        imt=10;
        wis=10;
        cha=10;
        dadoinicialHP=10;
        gold=10;
    }
};


class guerreiro:public personagem{//10% a mais de hp,e dano fisico.
   public:
    guerreiro(){
        str=4;
        dex=3;
        con=4;
        wis=1;
        imt=1;
        cha=1;
    }
};

//calsses darem buffs em % pros atributos.
    //lvl 1

int main(){
    personagem batata;
    guerreiro kaiqotario;
    batata.str=14;
    batata.espadaequipada.dano=10;
    printf("%d,%d,%d\n",batata.CalculaHP(),batata.con,batata.str);
    printf("%d,%d,%d",kaiqotario.CalculaHP(),kaiqotario.gold,kaiqotario.CalculaMana());
}

