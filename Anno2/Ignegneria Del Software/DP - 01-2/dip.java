class EmailService {
    public void inviaEmail(String messaggio) {
        System.out.println("Email inviata: " + messaggio);
    }
}

class NotificaManager {
    private EmailService emailService = new EmailService();

    public void inviaNotifica(String messaggio) {
        emailService.inviaEmail(messaggio);
    }
}


---------------

// Astratto: Interfaccia Servizio Notifica
interface ServizioNotifica {
    void invia(String messaggio);
}

// Implementazione concreta: EmailService
class EmailService implements ServizioNotifica {
    @Override
    public void invia(String messaggio) {
        System.out.println("Email inviata: " + messaggio);
    }
}

// Implementazione concreta: SmsService
class SmsService implements ServizioNotifica {
    @Override
    public void invia(String messaggio) {
        System.out.println("SMS inviato: " + messaggio);
    }
}

// Modulo di alto livello che dipende dall'astrazione
class NotificaManager {
    private ServizioNotifica servizioNotifica;

    public NotificaManager(ServizioNotifica servizioNotifica) {
        this.servizioNotifica = servizioNotifica;
    }

    public void inviaNotifica(String messaggio) {
        servizioNotifica.invia(messaggio);
    }
}

public class Main {
    public static void main(String[] args) {
        // Iniettiamo il tipo di servizio che vogliamo usare
        ServizioNotifica servizio = new EmailService(); // oppure new SmsService()
        NotificaManager manager = new NotificaManager(servizio);

        manager.inviaNotifica("Benvenuto nel sistema!");
    }
}

