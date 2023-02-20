
#include <stdio.h>
#include <stdlib.h>
#include <math.h>


class arma{
    public://simplificar por enquanto.
        int dano;
        char Tipo;
    /*/int UparArma(){
        dano+=dano;
    }/*/
    
    arma(){
        dano=10;
        Tipo='f';
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


class personagem{

    //unificar os mods de hp,stamina contara cm hit dice como no exemplo do homebrew.
    
    
    public:
        int lvl,str,dex,con,imt,wis,cha,stamina,gold,dadoinicialHP,HP,mana,HPregen,MPregen;
        char tipoddano;
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

    int CalculaDano(){
        return espadaequipada.dano+str+dex*10;
    }
    
    int CalculaArmor(){//ver como vao ficar os sclaes
        int armor=Calculabonus(str)+Calculabonus(dex)+Calculabonus(con);
        return ((str+con+dex+armor/2)+armaduraequipada.DefesaF)*5;
    }
     
     int CalculaMR(){
        int armor=Calculabonus(wis)+Calculabonus(imt)+Calculabonus(con);
        return wis+imt+con+armor/2;
    }

    int Resistdebuffmagico(){// sistema de darkest dungeon de %.
        return 0;
    }

     void setHP(int dano){
        HP=HP-dano;
    }

    int Dardano(personagem alvo){
        //if(tipoddano=='f'){
            if(alvo.CalculaArmor()>CalculaDano())
                return alvo.HP;
            alvo.HP=alvo.HP-CalculaDano()+alvo.CalculaArmor();
            return alvo.HP;
            if(alvo.HP<=0){
               
                gold+=alvo.gold;
            //}

        }else{

        }
        
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
        HP=CalculaHP();
        mana=CalculaMana();
        gold=10;
    }
};


class inimigo:public personagem{
    inimigo(){
        lvl=1;
        str=5;
        dex=5;
        con=5;
        imt=5;
        wis=10;
        cha=10;
        dadoinicialHP=10;
        gold=lvl*10;

    }

};

class guerreiro:public personagem{//10% a mais de hp,e dano fisico.
   public:
    guerreiro(){
        tipoddano='f';
        str=4;
        dex=3;
        con=4;
        wis=1;
        imt=1;
        cha=1;
    }
};

class skill{
    public:
        int dano,cura,efeito;

    int cura(personagem alvo){
        return alvo.con+cura;
    }
}; 


class jogo{
    public:
    personagem a,b;
    int fase,dificuldade;
    arma recompensa;
    


    void iniciaFase(){

        
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
    printf("KaiqOtario status\n Hp= %d\n",kaiqotario.HP);

    printf(
            "batata status\n Hp= %d\n",batata.CalculaHP());

    printf("%d\n", kaiqotario.HP);
    kaiqotario.HP=batata.Dardano(kaiqotario);
    printf("%d\n", kaiqotario.HP);
    printf("Dano = %d\n",(batata.espadaequipada.dano+batata.str+batata.dex)*10);
    kaiqotario.HP=batata.Dardano(kaiqotario);
    printf("%d\n", kaiqotario.HP);
}

