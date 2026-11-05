// Express 4 não encaminha rejeições de handlers async ao error handler.
module.exports = (handler) => (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);
