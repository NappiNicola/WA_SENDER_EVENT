function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    const title = data.title || "Evento senza titolo";
    const start = new Date(data.start);
    const end = new Date(data.end);
    const desc = data.description || "";

    // --- crea l'evento sul calendario ---
    const calendar = CalendarApp.getDefaultCalendar();
    const event = calendar.createEvent(title, start, end, { description: desc });

    // --- restituisci risposta JSON ---
    return ContentService.createTextOutput(
      JSON.stringify({ success: true, eventId: event.getId() })
    ).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ success: false, error: err.message })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}