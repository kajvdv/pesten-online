- [ ] Bij het laden van de site kan je een gebruikers naam kiezen
    - [ ] De server slaat de naam op in een cookie. Word niet meer naar gevraagd als dit cookie er al is.
    - [ ] Voorpagina vraagt alleen maar naam voor de user. Daarna redirect naar de lobbies
    - [ ] Uiteindelijk log in pagina om te registreren enzo

- [ ] Gebruikers kunnen lobbies maken
    - [ ] Gebruikers kunnen een naam aan de lobby geven
    - [ ] De hoeveelheid spelers instellen
    - [ ] Bij het joinen van de lobby kom je op de spelpagina.
            - [ ] Server respond met een token voor de websocket verbinding
        - [ ] Hier word weergeven hoeveel mensen er al in zitten. Dus de websocket verbinding word hier al gemaakt.
        - [ ] Als de laatste persoon binnen komt begint het spel en worden de berichten geaccepteerd.
    - [ ] Mogelijkheid om links naar games te delen om elkaar uit te nodigen
    
- [ ] Mogelijkheid om weer opnieuw verbinding te maken met de lobby als deze weg valt
    - [ ] Timeout wanneer de user te laat herverbind
    - [ ] De voorpagina laat zien aan welke spellen de gebruiker mee doet

- [ ] Spelers kunnen met elkaar chatten
    - [ ] Iets van chat.js maken die refereerd naar aantal classes/ids op de pagina
        - [ ] Een aparte websocket zorgt hiervoor

- [ ] Real time updates over wanneer spelers met de muis over de kaarten gaan.
    - [ ] Hier ook een aparte websocket voor maken

- [ ] Bij het aanmakan van een nieuw spel, zelf de regels bepalen
