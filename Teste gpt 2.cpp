#include <iostream>
#include <string>

class Arma {
  private:
    std::string nome_;
    int dano_;

  public:
    Arma(std::string nome, int dano) {
        nome_ = nome;
        dano_ = dano;
    }

    int getDano() const {
        return dano_;
    }

    std::string getNome() const {
        return nome_;
    }

    void setDano(int dano) {
        dano_ = dano;
    }

    void setNome(std::string nome) {
        nome_ = nome;
    }

    void atacar(Personagem& alvo) {
        std::cout << "A arma " << nome_ << " ataca " << alvo.getNome() << " e causa " << dano_ << " de dano!\n";
        alvo.receberDano(dano_);
    }
};

class Personagem {
  private:
    std::string nome_;
    int vida_;
    Arma arma_;

  public:
    Personagem(std::string nome, int vida, Arma arma) {
        nome_ = nome;
        vida_ = vida;
        arma_ = arma;
    }

    int getVida() const {
        return vida_;
    }

    std::string getNome() const {
        return nome_;
    }

    void setVida(int vida) {
        vida_ = vida;
    }

    void setNome(std::string nome) {
        nome_ = nome;
    }

    void setArma(Arma arma) {
        arma_ = arma;
    }

    void receberDano(int dano) {
        vida_ -= dano;
        std::cout << nome_ << " recebe " << dano << " de dano e tem " << vida_ << " de vida restante.\n";
    }

    void atacar(Personagem& alvo) {
        arma_.atacar(alvo);
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
