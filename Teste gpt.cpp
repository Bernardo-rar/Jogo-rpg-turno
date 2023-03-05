#include <iostream>
#include <vector>
#include <string>
#include <ctime>

using namespace std;

class Personagem {
public:
    string nome;
    int str, con, de, imt, cha, wis;
    int hp, mp;

    Personagem(string nome, int str, int con, int de, int imt, int cha, int wis, int hp, int mp) :
        nome(nome), str(str), con(con), de(de), imt(imt), cha(cha), wis(wis), hp(hp), mp(mp) {}

    void tomarDano(int dano) {
        hp -= dano;
    }

    void atacar(Personagem& alvo) {
        int dano = str;
        alvo.tomarDano(dano);
        cout << nome << " atacou " << alvo.nome << " causando " << dano << " de dano!\n";
    }
};

class Guerreiro : public Personagem {
public:
    Guerreiro(string nome, int str, int con, int de, int imt, int cha, int wis, int hp, int mp) :
        Personagem(nome, str, con, de, imt, cha, wis, hp, mp) {}

    void aumentarDefesa() {
        de += 5;
        cout << nome << " aumentou sua defesa!\n";
    }
};

class Mago : public Personagem {
public:
    Mago(string nome, int str, int con, int de, int imt, int cha, int wis, int hp, int mp) :
        Personagem(nome, str, con, de, imt, cha, wis, hp, mp) {}

    void bolaDeFogo(vector<Personagem>& inimigos) {
        int dano = 10 + imt;
        for (auto& inimigo : inimigos) {
            inimigo.tomarDano(dano);
            cout << nome << " lançou bola de fogo em " << inimigo.nome << " causando " << dano << " de dano!\n";
        }
    }
};

class Skill {
public:
    virtual void usarSkill(Personagem& personagem, vector<Personagem>& inimigos) = 0;
};

class Cura : public Skill {
public:
    void usarSkill(Personagem& personagem, vector<Personagem>& inimigos) override {
        int cura = personagem.wis;
        personagem.hp += cura;
        cout << personagem.nome << " se curou em " << cura << " pontos de vida!\n";
    }
};

class BolaDeFogo : public Skill {
public:
    void usarSkill(Personagem& personagem, vector<Personagem>& inimigos) override {
        if (Mago* mago = dynamic_cast<Mago*>(&personagem)) {
            mago->bolaDeFogo(inimigos);
        }
    }
};

class AumentarDefesa : public Skill {
public:
    void usarSkill(Personagem& personagem, vector<Personagem>& inimigos) override {
        if (Guerreiro* guerreiro = dynamic_cast<Guerreiro*>(&personagem)) {
            guerreiro->aumentarDefesa();
        }
    }
};

class Arma {
  public:
    enum TipoArma { Espada, Arco, Cajado, Adaga };
    Arma(TipoArma tipo = Espada) : tipo_(tipo) {}

    TipoArma GetTipo() const { return tipo_; }

    std::string GetNome() const {
        switch (tipo_) {
            case Espada: return "Espada";
            case Arco: return "Arco";
            case Cajado: return "Cajado";
            case Adaga: return "Adaga";
            default: return "";
        }
    }

    int GetDano() const {
        switch (tipo_) {
            case Espada: return 10;
            case Arco: return 8;
            case Cajado: return 6;
            case Adaga: return 12;
            default: return 0;
        }
    }

  private:
    TipoArma tipo_;
};