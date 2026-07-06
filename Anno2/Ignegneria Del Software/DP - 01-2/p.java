// 1. Interfaccia Prototype: dichiara clone()
interface Prototipo {
    Prototipo clona();
    void disegna();
}

// 1b. Classe astratta Forma: base comune per tutte le forme
abstract class Forma implements Prototipo {
    protected String colore;

    public Forma(String colore) {
        this.colore = colore;
    }

    @Override
    public abstract Prototipo clona();

    @Override
    public abstract void disegna();
}

// Support class: Bordo (oggetto collegato)
class Bordo {
    private String stile;

    public Bordo(String stile) {
        this.stile = stile;
    }

    public Bordo(Bordo bordo) {
        this.stile = bordo.stile;
    }

    public void disegnaBordo() {
        System.out.println("Con bordo: " + stile);
    }
}

// 2. Concrete Prototype: implementazione della clonazione

class Cerchio extends Forma {
    private int raggio;
    private Bordo bordo;

    public Cerchio(int raggio, String colore, Bordo bordo) {
        super(colore);
        this.raggio = raggio;
        this.bordo = bordo;
    }

    // Costruttore di copia
    public Cerchio(Cerchio sorgente) {
        super(sorgente.colore);
        this.raggio = sorgente.raggio;
        this.bordo = new Bordo(sorgente.bordo); // Clonazione profonda
    }

    @Override
    public Prototipo clona() {
        return new Cerchio(this);
    }

    @Override
    public void disegna() {
        System.out.println("Disegna un cerchio di raggio " + raggio + " e colore " + colore + ".");
        if (bordo != null) {
            bordo.disegnaBordo();
        }
    }
}

class Rettangolo extends Forma {
    private int larghezza;
    private int altezza;
    private Bordo bordo;

    public Rettangolo(int larghezza, int altezza, String colore, Bordo bordo) {
        super(colore);
        this.larghezza = larghezza;
        this.altezza = altezza;
        this.bordo = bordo;
    }

    // Costruttore di copia
    public Rettangolo(Rettangolo sorgente) {
        super(sorgente.colore);
        this.larghezza = sorgente.larghezza;
        this.altezza = sorgente.altezza;
        this.bordo = new Bordo(sorgente.bordo); // Clonazione profonda
    }

    @Override
    public Prototipo clona() {
        return new Rettangolo(this);
    }

    @Override
    public void disegna() {
        System.out.println("Disegna un rettangolo di " + larghezza + "x" + altezza + " e colore " + colore + ".");
        if (bordo != null) {
            bordo.disegnaBordo();
        }
    }
}

// 3. Main: client integrato
public class Main {
    public static void main(String[] args) {
        // Creo bordi
        Bordo bordoRosso = new Bordo("bordo rosso spesso");
        Bordo bordoBlu = new Bordo("bordo blu sottile");

        // Creo forme originali con bordi collegati
        Forma cerchio = new Cerchio(12, "rosso", bordoRosso);
        Forma rettangolo = new Rettangolo(40, 25, "blu", bordoBlu);

        // Clono e disegno direttamente
        Forma cerchioClonato = (Forma) cerchio.clona();
        Forma rettangoloClonato = (Forma) rettangolo.clona();

        cerchioClonato.disegna();
        rettangoloClonato.disegna();
    }
}
