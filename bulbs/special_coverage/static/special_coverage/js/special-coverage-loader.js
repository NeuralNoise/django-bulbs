module.exports = (function () { // eslint-disable-line no-unused-vars
  var _ = require('lodash');
  var assign = _.assign;
  var defaults = _.defaults;
  var isUndefined = _.isUndefined;
  var trim = _.trim;

  function requireArgument (value, message) {
    if (isUndefined(value)) { throw new Error(message); }
  }

  function SpecialCoverageLoader (element, listElement, options) {
    requireArgument(element, 'new SpecialCoverageLoader(element, listElement, options): element is undefined');
    requireArgument(listElement, 'new SpecialCoverageLoader(element, listElement, options): listElement is undefined');
    requireArgument(element.dataset.total, 'new SpecialCoverageLoader(element, listElement, options): element has no data-total value');
    requireArgument(element.dataset.perPage, 'new SpecialCoverageLoader(element, listElement, options): element has no data-per-page value');

    options = options || {};
    this.total = parseInt(element.dataset.total, 10);
    this.perPage = parseInt(element.dataset.perPage, 10);
    this.currentPage = 1;
    this.listElement = listElement;
    this.element = element;

    console.log('list items: ' + this.listElement.children.length);
    console.log('total: ' + this.total);
    console.log('per_page: ' + this.perPage);

    defaults(options, {
      baseUrl: window.location.href,
    });

    assign(this, options);

    element.addEventListener('click', function () {
      var url = this.buildUrl(this.currentPage, this.perPage, this.baseUrl);
      this.loadMore(url);
    }.bind(this));
  }

  assign(SpecialCoverageLoader.prototype, {
    nextOffset: function (currentPage, perPage) {
      requireArgument(currentPage, 'SpecialCoverageLoader.nextOffset(currentPage, perPage): currentPage is undefined');
      requireArgument(perPage, 'SpecialCoverageLoader.nextOffset(currentPage, perPage): perPage is undefined');

      return currentPage * perPage;
    },

    buildUrl: function (currentPage, perPage, baseUrl) {
      requireArgument(currentPage, 'SpecialCoverageLoader.buildUrl(currentPage, perPage, baseUrl, offset): currentPage is undefined');
      requireArgument(perPage, 'SpecialCoverageLoader.buildUrl(currentPage, perPage, baseUrl, offset): perPage is undefined');
      requireArgument(baseUrl, 'SpecialCoverageLoader.buildUrl(currentPage, perPage, baseUrl, offset): baseUrl is undefined');

      var offset = this.nextOffset(currentPage, perPage);

      return [baseUrl, 'more', offset].join('/');
    },

    loadMore: function (url) {
      requireArgument(url, 'SpecialCoverageLoader.loadMore(url): url is undefined');

      $.ajax({
        url: url,
        type: 'get',
        dataType: 'html',
      })
        .done(this.handleLoadMoreSuccess.bind(this))
        .fail(this.handleLoadMoreFailure.bind(this));
    },

    handleLoadMoreSuccess: function (response) {
      requireArgument(response, 'SpecialCoverageLoader.handleLoadMoreSuccess(response): response is undefined');

      response = trim(response);
      if (response) {
        this.currentPage += 1;
        this.listElement.innerHTML = this.listElement.innerHTML + response;
      }
      console.log('list items: ' + this.listElement.children.length);
      this.setButtonVisibility(response);
    },

    handleLoadMoreFailure: function (response) {
      requireArgument(response, 'SpecialCoverageLoader.handleLoadMoreFailure(response): response id undefined');

      var message = [
        'SpecialCoverageLoader.loadMore("',
        this.buildUrl(this.currentPage, this.perPage, this.baseUrl),
        '"): server responded with "',
        response.status,
        ' ',
        response.statusText,
        '"',
      ].join('');

      console.log(message);
    },

    hideElement: function () {
      this.element.style.display = 'none';
    },

    isLastPage: function (total, listElement) {
      requireArgument(total, 'SpecialCoverageLoader.isLastPage(total, listElement): total is undefined');
      requireArgument(listElement, 'SpecialCoverageLoader.isLastPage(total, listElement): listElement is undefined');

      return total === listElement.children.length;
    },

    setButtonVisibility: function (response) {
      requireArgument(response, 'SpecialCoverageLoader.setButtonVisibility(response): response is undefined');

      if (!response || this.isLastPage(this.total, this.listElement)) {
        this.hideElement();
      }
    },
  });
  return SpecialCoverageLoader;
})();
