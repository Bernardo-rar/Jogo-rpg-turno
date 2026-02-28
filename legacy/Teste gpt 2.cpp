#include <iostream>
#include <string>

class Arma {
  private:
    string nome[20];
    int dano;

  public:
    Arma(std::string nome, int dano) {
        nome = nome;
        dano = dano;
    }

    int getDano() const {
        return dano;
    }

    std::string getNome() const {
        return nome;
    }

    void setDano(int dano) {
        dano = dano;
    }

    void setNome(std::string nome) {
        nome = nome;
    }

    void atacar(Personagem& alvo) {
        std::cout << "A arma " << nome << " ataca " << alvo.getNome() << " e causa " << dano_ << " de dano!\n";
        alvo.receberDano(dano);
    }
};

class Personagem {
  private:
    string nome[20];
    int vida;
    Arma arma;

  public:
    Personagem(string nome, int vida, Arma arma) {
        nome = nome;
        vida = vida;
        arma = arma;
    }

    int getVida() const {
        return vida;
    }

    std::string getNome() const {
        return nome;
    }

    void setVida(int vida) {
        vida = vida;
    }

    void setNome(std::string nome) {
        nome= nome;
    }

    void setArma(Arma arma) {
        arma= arma;
    }

    void receberDano(int dano) {
        vida-= dano;
        std::cout << nome << " recebe " << dano << " de dano e tem " << vida_ << " de vida restante.\n";
    }

    void atacar(Personagem& alvo) {
        arma.atacar(alvo);
    }
};

int main() {
    Arma espada("Espada longa", 10);
    Personagem guerreiro("Guerreiro", 100, espada);
    Personagem monstro("Monstro", 50, Arma("Garras afiadas", 5));

    guerreiro.atacar(monstro);
    monstro.atacar(guerreiro);

    return 0;
}
