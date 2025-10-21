function doGet(e) {
  var calendar = CalendarApp.getDefaultCalendar();

  // Data di domani
  var now = new Date();
  var start = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 0);
  var end = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 2, 0, 0, 0);

  // Legge gli eventi di domani
  var events = calendar.getEvents(start, end);
  var data = [];

  for (var i = 0; i < events.length; i++) {
    var ev = events[i];
    data.push({
      title: ev.getTitle(),
      description: ev.getDescription(),
      start: ev.getStartTime(),
      end: ev.getEndTime()
    });
  }

  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
