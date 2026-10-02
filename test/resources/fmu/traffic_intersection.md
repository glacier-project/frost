# Cosimulare i semafori

L'incrocio usa **cinque FMU FMI 3.0 Co-Simulation** nella cartella
[`fmus/`](../fmus): un controllore e quattro semafori indipendenti.
Il master di cosimulazione trasferisce i comandi dal controllore ai semafori.

## Avvio rapido

Dalla radice del progetto, con le dipendenze di `requirements.txt` installate
nell'ambiente `.venv`:

```bash
.venv/bin/python examples/traffic_intersection.py --stop-time 60 --step-size 0.1
```

Lo script usa FMPy e stampa in CSV i cambi di luce, senza interfaccia grafica.
Per salvare il risultato, aggiungere `> traffic.csv` al comando.
Gli archivi sono già disponibili; per ricostruirli e verificarli:

```bash
.venv/bin/python build_traffic.py
.venv/bin/python tests/test_Traffic.py
```

Questi FMU richiedono un runtime Python compatibile con `pythonfmu3` anche
quando vengono caricati da un altro master.

## Collegamenti

Importare i cinque archivi e collegare le uscite **Int32** di
`TrafficController.fmu` all'ingresso **Int32** `command` di ciascun semaforo:

| Uscita del controllore | FMU destinatario | Ingresso |
|---|---|---|
| `north_command` | `TrafficLightNorth.fmu` | `command` |
| `south_command` | `TrafficLightSouth.fmu` | `command` |
| `east_command` | `TrafficLightEast.fmu` | `command` |
| `west_command` | `TrafficLightWest.fmu` | `command` |

Non servono collegamenti di ritorno. Ogni semaforo espone `color`
(`0` spento, `1` rosso, `2` giallo, `3` verde) e le uscite Boolean
`red`, `yellow`, `green`, `fault`. Un comando non valido produce rosso e
`fault=true`; un comando valido successivo rimuove l'errore.

## Ordine di esecuzione del master

1. Istanziare e inizializzare tutti i FMU allo stesso tempo iniziale
   (l'esempio parte da `t=0`).
2. Leggere i quattro comandi del controllore e scriverli nei rispettivi
   semafori, poi leggere le luci. Le uscite dei semafori cambiano subito
   quando viene impostato `command`.
3. Scegliere il passo come il minimo tra il passo desiderato,
   `TrafficController.phase_remaining` e il tempo rimasto alla fine della
   simulazione. Questo evita di saltare transizioni.
4. Eseguire `doStep` sui quattro semafori e sul controllore con lo stesso
   tempo e passo; avanzare il tempo e ripetere dal punto 2.
5. Al tempo finale, trasferire ancora i comandi e leggere le luci, poi
   terminare e liberare tutte le istanze.

Trasferire sempre tutti e quattro i comandi prima di osservare l'incrocio.
Lo script [`traffic_intersection.py`](traffic_intersection.py) implementa
questa sequenza.

## Tempi e comandi

Il ciclo predefinito dura **30 secondi**:

| Intervallo | Nord / Sud | Est / Ovest |
|---|---|---|
| 0–2 s | Rosso | Rosso |
| 2–12 s | Verde | Rosso |
| 12–15 s | Giallo | Rosso |
| 15–17 s | Rosso | Rosso |
| 17–27 s | Rosso | Verde |
| 27–30 s | Rosso | Giallo |

Per modificare i tempi, impostare i parametri Float64 del controllore
**prima di uscire dall'inizializzazione**: `ns_green_time` e `ew_green_time`
(default 10 s), `yellow_time` (3 s), `all_red_time` (2 s).
Devono essere finiti e strettamente positivi. Lo script di esempio usa i
valori predefiniti; la sua CLI permette di cambiare durata e passo della
simulazione, non questi parametri.

Gli ingressi Boolean `enabled=false` oppure `emergency_stop=true` comandano
tutto rosso al successivo `doStep`. Alla riabilitazione, il ciclo riparte
dall'intero intervallo iniziale di tutto rosso. Il modello è a ciclo fisso,
senza pedoni o sensori di traffico.
