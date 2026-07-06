import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import sys

DIM = 1000  # dimensione warp
def crop(filename, n_rows, n_cols):
    # Carica e trova la griglia
    img = cv2.imread(filename)
    if img is None: 
        print("Img not found")
        sys.exit()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #conversione da scala di colori a scala di grigi 
    _, negative_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU) #otsu calcola automaticamente la soglia di colori ottimale

    find_contours , _= cv2.findContours(negative_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #retr external considera solo il perimetro esterno escludendo la parte interna, chainApprox che comprime segmenti lineari, prende solo gli estremi di una linea 
    find_biggest_contours  = sorted(find_contours, key=cv2.contourArea, reverse=True) #la funzione sorted ordina in ordine decrescente i valori trovati (reverse = True)

    if not find_biggest_contours: 
        print("Grid not found")
        sys.exit()

    def order_points(corners):
        TL_BR = corners.sum(1) #Top Left e Bottom Right; somma x e y per ogni angolo
        TR_BL = (corners[:,0] - corners[:,1]) #è come se facessi x - y iterando i signoli valori
        src = np.float32([corners[np.argmin(TL_BR)], corners[np.argmax(TR_BL)], corners[np.argmax(TL_BR)], corners[np.argmin(TR_BL)]])
        return src

    corners = None

    c = find_biggest_contours[0] #prendo contorno più grande
    corners = cv2.boxPoints(cv2.minAreaRect(c)).astype(np.float32) #BoxPoints serve a raddrizzare la griglia prima di tagliare le celle, restituisce 4 angoli partendo dal centro la dimensione e l'angolo restituiti da minAreaReact; minAreaReact usa un rettangolo ruotato, per aderire perfettamente al bordo dell'input passato
    src = order_points(corners)
    dst = np.float32([[0,0],[DIM-1,0],[DIM-1,DIM-1],[0,DIM-1]])
    warped = cv2.warpPerspective(gray, cv2.getPerspectiveTransform(src, dst), (DIM, DIM))
    warped = cv2.morphologyEx(
    cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1],
        cv2.MORPH_OPEN, np.ones((3,3), np.uint8))


    # 2. Trova intervalli celle con estrazione morfologica delle linee
    def get_intervals(warped_img, n, direction):
        """
        Trova gli intervalli delle celle isolando le linee della griglia
        con apertura morfologica, poi definendo le celle come gap tra le linee.
        direction: 'h' per righe (linee orizzontali), 'v' per colonne (linee verticali)
        """

        expected_size = DIM / n 
        MARGIN = 2# pixel di margine per evitare residui della griglia

        #usiamo un kernel per morfologia matematica (tecnica basata sulla geometria, forma, dimesione e relazioni spaziali tra oggetti)
        kernel_len = max(int(expected_size * 0.3), 40) #calcolo la lunghezza della maschera (o kernel)
        if direction == 'h':
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1)) #crea un kernel rettangolare lungo kernel_len e alto 1 agendo solo nell'asse orizzontale
            lines_only = cv2.morphologyEx(warped_img, cv2.MORPH_OPEN, kernel) #prendiamo solo le linee dato che Open usa il kernel come test ovvero cancellando ogni macchia bianca dove il kernel non riesce ad entrare completamente
            proj = lines_only.sum(axis=1).astype(float) #lines_only è un immagine binaria somma degli dei pixel axis 1 per la riga
        else:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
            lines_only = cv2.morphologyEx(warped_img, cv2.MORPH_OPEN, kernel)
            proj = lines_only.sum(axis=0).astype(float)

        #se non trova le righe, divisione matematica
        if proj.max() == 0:
            return [(int(i * expected_size), int((i + 1) * expected_size)) for i in range(n)]

        #Soglia per individuare dove ci sono linee nella proiezione
        threshold = proj.max() * 0.3
        is_line = proj > threshold #creo una sequenza di true e false per capire dove iniziano e finiscono le righe 

        #Trova segmenti contigui di linea (inizio e fine di ciascuno)
        padded = np.concatenate([[False], is_line, [False]])#aggiungo un pad per considerare anche il caso che la linea parte dal pixel 0 e rilevare il salto 
        diff = np.diff(padded.astype(int)) #[0, 0, +1, 0, 0, -1, 0, 0]
        line_starts = np.where(diff == 1)[0]
        line_ends = np.where(diff == -1)[0]

        # Le celle sono i gap tra linee consecutive
        # Confini: [0, s0, e0, s1, e1, ..., sN, eN, DIM]
        boundaries = [0]#parte da zero
        for s, e in zip(line_starts, line_ends):
            boundaries.append(int(s))
            boundaries.append(int(e))
        boundaries.append(DIM)#arriva a DIM

        gaps = []
        for i in range(0, len(boundaries) - 1, 2): #salto a due a due 
            g_start = boundaries[i] + MARGIN
            g_end = boundaries[i + 1] - MARGIN
            if g_end > g_start and (g_end - g_start) > expected_size * 0.15:
                gaps.append((g_start, g_end))

        # Fallback se non trova abbastanza gap
        if len(gaps) < n:
            return [(int(i * expected_size), int((i + 1) * expected_size)) for i in range(n)]

        # Seleziona i gap più vicini alla dimensione attesa, poi riordina per posizione
        gaps.sort(key=lambda g: abs((g[1] - g[0]) - expected_size)) #ordinati per bontà della misura più simile a expected
        return sorted(gaps[:n], key=lambda g: g[0]) #Dobbiamo rimetterli in ordine di posizione, dal pixel 0 in poi key=lambda g: g[0] dice: "Ordina usando il punto di inizio dell'intervallo

    # Richiamo: passa l'immagine warpata e la direzione
    rows = get_intervals(warped, n_rows, 'h')
    cols = get_intervals(warped, n_cols, 'v')

    # 3. Pulisci ogni cella 
    def clean_cell(cell):
        cell[:1,:] = cell[-1:,:] = cell[:,:1] = cell[:,-1:] = 0 #creo un bordo nero per eliminare possibile rumore 
        n, labels, stats, _ = cv2.connectedComponentsWithStats(cell) #analizza immagine e raggruppa pixel bianchi che si trovano vicini tra loro
        if n < 2: 
            return np.zeros((28,28), np.uint8) #se l'isola è troppo piccola mettiamo direttamente lo sfondo nero

        best_idx = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])   #con stats prendo le informazioni sulle "isole" (pixel) a partire dall'isola 1 
                                                                #(0 sarebbe l'area più grande ovvero lo sfondo nero). cv2CC_STAT dice di considerare tutto
                                                                #il blocco di pixel uniti (area) che verrà preso da argmax. Aggiungo 1 per la colonna 
                                                                #aggiunta intorno. Returna l'indice dell'isola maggiore trovata

        x, y, w, h, area = stats[best_idx]  #x,y coordinate ancgolo in alto a sinistra del rettangolo che contene l'oggetto
                                            #w larghezza del rettangolo, h altezza del rettangolo
        if area < 50: #se isola è troppo piccola allora è rumore, setto a nero
            return np.zeros((28, 28), np.uint8)
        rapporto = w / h
        if rapporto > 5 or rapporto < 0.2: #se l'area è molto sproporzionata in lunghezza o larghezza setto a nero
            return np.zeros((28, 28), np.uint8)
        
        H_cell, W_cell = cell.shape
        is_vertical_line = w < 6 and (h > H_cell * 0.5) #se l'oggetto è molto fino ma anche lungo allora fa parte della griglia verticale
        is_horizontal_line = h < 6 and (w > W_cell * 0.5) #se l'oggetto è molto fino ma anche largo allora fa parte della linea orizzonatale
        if is_vertical_line or is_horizontal_line:
            return np.zeros((28, 28), np.uint8)
        digit = (labels[y:y+h, x:x+w] == best_idx).astype(np.uint8) * 255   #ritaglio dalla mapp solo il rettangolo in cui si trova la lettera (ottengo una nuova mappa con TRUE e FALSE)
                                                                            #faccio casting a 0,1 e moltiplico per 255 per avere il bianco
        
        # Calcola quanto bordo nero aggiungere sopra/sotto e destra/sinistra
        bordo = max(w, h) + 6 #il qudrato deve essere lungo almeno quanto il lato più lungo della lettera, 6 è quello che aggiungo per dare spazio
        dy, dx = (bordo - h), (bordo - w)
        pad=0
        # Aggiungi i bordi: ((Top, Bottom), (Left, Right))
        square = np.pad(digit, ((dy//2+pad, dy - dy//2+pad), (dx//2+pad, dx - dx//2+pad)))  # np.pad va a riempire sopra sotto, destra/sinistra di pixel neri fino a raggiungere lo spazio desiderato
                                                                            # questo lo rappresento con una tupla di tuple ((sopra, sotto), (sinistra, destra))

        return cv2.resize(square, (28, 28), interpolation=cv2.INTER_AREA) #interpolation è un metodo matematico per evitare di avere linee troppo pixelose quando vado a ridimensionare l'immagine

    # --- 4. Estrai tutte le celle ---
    cells = []
    for i, r in enumerate(rows[:n_rows]):
        for j, c in enumerate(cols[:n_cols]):
            cells.append((i, j, clean_cell(warped[r[0]:r[1], c[0]:c[1]])))  #dove i è il numero della riga, j della colonna r[0]:R[1] dimensione della cella rispetto alla riga relativamente la stessa cosa per c 
    #print(cells[0])
    return cells

if __name__ == "__main__":
    n_rows = 5
    n_cols = 5
    cells = crop("prova5.png", n_rows, n_cols )
    # --- 5. Visualizza griglia ---
    fig1, axes = plt.subplots(n_rows, n_cols, figsize=(8,8))
    for i, j, cell in cells:
        axes[i, j].imshow(cell, cmap="gray")
        axes[i, j].axis("off")
    plt.tight_layout()

    # --- 6. Visualizza cella singola con slider ---
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    plt.subplots_adjust(bottom=0.2) #spazio in basso per slider
    im = ax2.imshow(cells[0][2], cmap="gray")
    ax2.axis("off")
    title = ax2.set_title(f"Cella (0, 0) — 1/{len(cells)}")

    slider_ax = fig2.add_axes([0.15, 0.06, 0.7, 0.04])
    slider = Slider(slider_ax, "Cella", 0, len(cells)-1, valinit=0, valstep=1)

    def update(val):
        idx = int(slider.val)
        i, j, cell = cells[idx]
        im.set_data(cell)
        ax2.set_title(f"Cella ({i}, {j}) — {idx+1}/{len(cells)}")
        fig2.canvas.draw_idle()

    slider.on_changed(update)

    def on_key(event):
        if event.key == "right" and slider.val < len(cells)-1:
            slider.set_val(slider.val + 1)
        elif event.key == "left" and slider.val > 0:
            slider.set_val(slider.val - 1)

    fig2.canvas.mpl_connect("key_press_event", on_key)

    plt.show()