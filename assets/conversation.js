// Change these settings to control every conversation timestamp.
const conversationDateFormat = {
  timeZone: "UTC", // Use undefined to show the browser's local time zone.
  dateSeparator: "-",
  dateTimeSeparator: " ",
  timeSeparator: ":",
  includeSeconds: true,
};

function formatConversationDate(date) {
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone: conversationDateFormat.timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  });
  const parts = Object.fromEntries(
    formatter
      .formatToParts(date)
      .filter(({ type }) => ["year", "month", "day", "hour", "minute", "second"].includes(type))
      .map(({ type, value }) => [type, value]),
  );
  const dateText = [parts.year, parts.month, parts.day].join(conversationDateFormat.dateSeparator);
  const timeParts = [parts.hour, parts.minute];
  if (conversationDateFormat.includeSeconds) {
    timeParts.push(parts.second);
  }
  return `${dateText}${conversationDateFormat.dateTimeSeparator}${timeParts.join(conversationDateFormat.timeSeparator)}`;
}

document.querySelectorAll("time[data-timestamp]").forEach((element) => {
  const date = new Date(element.dataset.timestamp);
  if (!Number.isNaN(date.valueOf())) {
    element.textContent = formatConversationDate(date);
  }
});
