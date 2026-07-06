// Rettangolo.java
public class Rettangolo {
    protected int larghezza;
    protected int altezza;

    public void setLarghezza(int larghezza) {
        this.larghezza = larghezza;
    }

    public void setAltezza(int altezza) {
        this.altezza = altezza;
    }

    public int getArea() {
        return larghezza * altezza;
    }
}

// Quadrato.java
public class Quadrato extends Rettangolo {
    @Override
    public void setLarghezza(int larghezza) {
        this.larghezza = larghezza;
        this.altezza = larghezza;
    }

    @Override
    public void setAltezza(int altezza) {
        this.larghezza = altezza;
        this.altezza = altezza;
    }
}

// Main.java
public class Main {
    public static void main(String[] args) {
        // Uso un Rettangolo
        Rettangolo r = new Rettangolo();
        r.setLarghezza(5);
        r.setAltezza(10);
        System.out.println("Area del rettangolo: " + r.getArea()); // 50

        // Uso un Quadrato come se fosse un Rettangolo
        Rettangolo q = new Quadrato();
        q.setLarghezza(5);
        q.setAltezza(10);
        System.out.println("Area del quadrato: " + q.getArea()); // Problema! Stampa 100 invece di 50
    }
}
