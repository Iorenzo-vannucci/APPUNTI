// 1. Prodotti Astratti: dichiarano interfacce per prodotti correlati
interface Chair {
    void sitOn();
}

interface Sofa {
    void lieOn();
}

interface CoffeeTable {
    void placeItems();
}

// 2. Prodotti Concreti: implementazioni specifiche delle interfacce, raggruppate per variante
// --- Modern ---
class ModernChair implements Chair {
    @Override
    public void sitOn() {
        System.out.println("Ti siedi su una sedia moderna elegante.");
    }
}

class ModernSofa implements Sofa {
    @Override
    public void lieOn() {
        System.out.println("Ti sdrai su un divano moderno comodo.");
    }
}

class ModernCoffeeTable implements CoffeeTable {
    @Override
    public void placeItems() {
        System.out.println("Appoggi oggetti su un tavolino moderno minimalista.");
    }
}

// --- Victorian ---
class VictorianChair implements Chair {
    @Override
    public void sitOn() {
        System.out.println("Ti siedi su una sedia vittoriana riccamente decorata.");
    }
}

class VictorianSofa implements Sofa {
    @Override
    public void lieOn() {
        System.out.println("Ti sdrai su un divano vittoriano classico.");
    }
}

class VictorianCoffeeTable implements CoffeeTable {
    @Override
    public void placeItems() {
        System.out.println("Appoggi oggetti su un tavolino vittoriano ornato.");
    }
}

// --- ArtDeco ---
class ArtDecoChair implements Chair {
    @Override
    public void sitOn() {
        System.out.println("Ti siedi su una sedia ArtDeco dallo stile geometrico.");
    }
}

class ArtDecoSofa implements Sofa {
    @Override
    public void lieOn() {
        System.out.println("Ti sdrai su un divano ArtDeco elegante.");
    }
}

class ArtDecoCoffeeTable implements CoffeeTable {
    @Override
    public void placeItems() {
        System.out.println("Appoggi oggetti su un tavolino ArtDeco raffinato.");
    }
}

// 3. Abstract Factory: dichiara metodi per creare i prodotti astratti
interface FurnitureFactory {
    Chair createChair();
    Sofa createSofa();
    CoffeeTable createCoffeeTable();
}

// 4. Factory Concrete: implementano l’Abstract Factory
class ModernFurnitureFactory implements FurnitureFactory {
    @Override
    public Chair createChair() {
        return new ModernChair();
    }

    @Override
    public Sofa createSofa() {
        return new ModernSofa();
    }

    @Override
    public CoffeeTable createCoffeeTable() {
        return new ModernCoffeeTable();
    }
}

class VictorianFurnitureFactory implements FurnitureFactory {
    @Override
    public Chair createChair() {
        return new VictorianChair();
    }

    @Override
    public Sofa createSofa() {
        return new VictorianSofa();
    }

    @Override
    public CoffeeTable createCoffeeTable() {
        return new VictorianCoffeeTable();
    }
}

class ArtDecoFurnitureFactory implements FurnitureFactory {
    @Override
    public Chair createChair() {
        return new ArtDecoChair();
    }

    @Override
    public Sofa createSofa() {
        return new ArtDecoSofa();
    }

    @Override
    public CoffeeTable createCoffeeTable() {
        return new ArtDecoCoffeeTable();
    }
}

// 5. Client: usa la factory tramite interfacce astratte, senza dipendere dalle implementazioni concrete
public class Main {
    public static void main(String[] args) {
        // Scegli la famiglia di mobili da creare
        FurnitureFactory factory = new VictorianFurnitureFactory(); // oppure ModernFurnitureFactory, ArtDecoFurnitureFactory

        Chair chair = factory.createChair();
        Sofa sofa = factory.createSofa();
        CoffeeTable coffeeTable = factory.createCoffeeTable();

        chair.sitOn();
        sofa.lieOn();
        coffeeTable.placeItems();
    }
}
