// Costanti condivise da tutti i moduli.

const CATEGORIE = [
  { id: "lavoro", label: "Lavoro" },
  { id: "legale", label: "Legale" },
  { id: "personale", label: "Personale" },
  { id: "casa-auto", label: "Casa e auto" },
  { id: "altro", label: "Altro" },
];

const CATEGORIA_PER_ID = Object.fromEntries(CATEGORIE.map((c) => [c.id, c]));
const CATEGORIA_PREDEFINITA = "altro";

const VISTE = ["prossimi", "settimana", "completati"];
const VISTA_PREDEFINITA = "prossimi";

// Collezione del database dell'artifact (numero dispari di segmenti).
const COLLEZIONE = "impegni";

// Chiave usata quando l'app gira fuori da claude.ai (file aperto in locale).
const STORAGE_KEY = "agenda-daniele/impegni/v1";

const DURATA_NOTIFICA_MS = 5000;
