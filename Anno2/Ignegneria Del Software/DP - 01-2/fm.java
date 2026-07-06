// 1. Product: definisce l'interfaccia comune
interface Transport {
    void deliver();
}

// 2. Concrete Products: implementazioni specifiche di Transport
class Truck implements Transport {
    @Override
    public void deliver() {
        System.out.println("Consegna delle merci su strada tramite camion.");
    }
}

class Ship implements Transport {
    @Override
    public void deliver() {
        System.out.println("Consegna delle merci via mare tramite nave.");
    }
}

// 3. Creator: dichiara il factory method
abstract class Logistics {
    public abstract Transport createTransport();
}

// 4. Concrete Creators: sovrascrivono il factory method
class RoadLogistics extends Logistics {
    @Override
    public Transport createTransport() {
        return new Truck();
    }
}

class SeaLogistics extends Logistics {
    @Override
    public Transport createTransport() {
        return new Ship();
    }
}

public class Main {
    public static void main(String[] args) {
        // Scegli la logistica da usare
        Logistics logistic = new RoadLogistics(); // oppure new SeaLogistics()

        Transport transport = logistic.createTransport();
        transport.deliver();
    }
}
