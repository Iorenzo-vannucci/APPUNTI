public class Configurazione {
    // 1. Campo statico privato per l'unica istanza
    private static Configurazione istanza;

    // 2. Alcuni dati di configurazione
    private String impostazione;

    // 3. Costruttore privato: vietato istanziare dall'esterno
    private Configurazione() {
        impostazione = "Impostazione di default";
    }

    // 4. Metodo pubblico statico per accedere all'istanza
    public static Configurazione getIstanza() {
        if (istanza == null) {
            istanza = new Configurazione();
        }
        return istanza;
    }

    // 5. Metodi di uso
    public String getImpostazione() {
        return impostazione;
    }

    public void setImpostazione(String nuovaImpostazione) {
        impostazione = nuovaImpostazione;
    }
}

// Main: utilizzo del Singleton
public class Main {
    public static void main(String[] args) {
        // Primo accesso al Singleton
        Configurazione config1 = Configurazione.getIstanza();
        System.out.println("Impostazione iniziale: " + config1.getImpostazione()); // Impostazione di default
        // Cambio l'impostazione
        config1.setImpostazione("Modalità scura attivata");

        // Secondo accesso al Singleton
        Configurazione config2 = Configurazione.getIstanza();
        System.out.println("Impostazione letta da una nuova variabile: " + config2.getImpostazione()); // Modalità scura attivata

        // Verifica: sono lo stesso oggetto?
        System.out.println("config1 e config2 sono lo stesso oggetto? " + (config1 == config2)); // true
    }
}
