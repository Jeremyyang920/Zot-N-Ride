API_URL = 'https://zot-n-ride-dev.herokuapp.com';

angular.module('zotnride.controllers', [])

.controller('AppCtrl', function($scope, $ionicModal, $rootScope, $window, $timeout, $ionicHistory, $ionicPlatform, $ionicPopup, $http, $cordovaGeolocation, $cordovaDatePicker) {

  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //$scope.$on('$ionicView.enter', function(e) {
  //});

  // Form data for the login modal
  $scope.loginData = {};
  $scope.user = JSON.parse($window.localStorage.getItem('user'));
  $scope.requests = [
    {
      "toSchool": { "time": "123", "riderInfo": "tvwong", leaveAt: "120" }, 
      "fromSchool": { "time": "234", "riderInfo": "jeremy" } 
    },
    {
      "toSchool": { "time": "123", "riderInfo": "anuj", leaveAt: "120" }, 
      "fromSchool": { "time": "234", "riderInfo": "meetp" } 
    },
    {
      "toSchool": { "time": "123", "riderInfo": "anuj", leaveAt: "120" }, 
      "fromSchool": { "time": "234", "riderInfo": "meetp" } 
    }
  ];

  $ionicModal.fromTemplateUrl('templates/login.html', {
    scope: $scope,
    animation: 'slide-in-up'
  }).then(function(modal) {
    $scope.loginModal = modal;

    if (!$scope.user || typeof $scope.user === undefined) {
      $scope.loginModal.show();
    }
  });

  $scope.closeLogin = function() {
    $scope.loginModal.hide();
    if ($ionicHistory.currentView().title === 'Registration')
      $ionicHistory.backView().go();
  };

  $scope.showLogin = function() {
    $scope.loginModal.show();
  };

  $scope.showRequests = function() {
    $ionicModal.fromTemplateUrl('templates/requests.html', {
      scope: $scope,
      animation: 'slide-in-up'
    }).then(function(modal) {
      $scope.requestModal = modal;
      $scope.requestModal.show();
    })
  };
  
  $scope.closeRequests = function() {
    $scope.requestModal.hide();
  }

  // Reserve Modal
  $ionicModal.fromTemplateUrl('templates/reserve.html', {
    scope: $scope,
    animation: 'slide-in-up'
  }).then(function(modal) {
    $scope.reserveModal = modal;
  });

  $scope.closeReserve = function() {
    $scope.reserveModal.hide();
  };

  $scope.showReserve = function() {
    if (window.localStorage.getItem('uid') === null || window.localStorage.getItem('uid') === '') {
      $scope.loginModal.show();
    } else
    $scope.reserveModal.show();
  };

  // Perform login
  $scope.doLogin = function() {
    $http({
      method: 'POST',
      url: API_URL + '/api/login',
      data: {
        netID: $scope.loginData.email,
        password: $scope.loginData.password
      },
      headers: {'Content-Type': 'application/json'}
    }).then(function successCallback(response) {
      $window.localStorage.setItem('user', JSON.stringify(response.data));
      $scope.loginModal.hide();
    }, function errorCallback(response) {
      $scope.showLoginFailedAlert = function() {
        var alertPopup = $ionicPopup.alert({
          title: 'Login Failed',
          template: 'Email/password is incorrect.'
        });
      };

      $scope.showLoginFailedAlert();
    });
  };

  var getDayString = function(day) {
    switch(day) {
      case 0:
      case 1:
      case 6:
      case 7:
        return 'Mon';
      case 2:
        return 'Tue';
      case 3:
        return 'Wed';
      case 4:
        return 'Thu';
      case 5:
        return 'Fri';
    }
  }

  // Autofill schedule
  if ($scope.user.arrivals) {
    var day = new Date().getDay();
    var dayString = getDayString(day);

    var dateObj = moment($scope.user.arrivals[dayString], 'Hmm');

    if (dateObj < moment()) {
      dayString = getDayString(day + 1);
      $scope.arrivalTime = moment($scope.user.arrivals[dayString], 'Hmm').add(1, 'day');
      
      if (day === 5) {
        $scope.arrivalTime = $scope.arrivalTime.add(2, 'day');
      } else if (day === 6) {
        $scope.arrivalTime = $scope.arrivalTime.add(1, 'day');
      }
    } else {
      $scope.arrivalTime = dateObj;
    }
  } else {
    $scope.arrivalTime = moment().add(1, 'hours').minute(0).second(0);
  }

  if ($scope.user.departures) {
    var day = new Date().getDay();
    var dayString = getDayString(day);

    var dateObj = moment($scope.user.departures[dayString], 'Hmm');

    if (dateObj < moment()) {
      dayString = getDayString(day + 1);
      $scope.departureTime = moment($scope.user.departures[dayString], 'Hmm').add(1, 'day');

      if (day === 5) {
        $scope.departureTime = $scope.departureTime.add(2, 'day');
      } else if (day === 6) {
        $scope.departureTime = $scope.departureTime.add(1, 'day');
      }
    } else {
      $scope.departureTime = dateObj;
    }
  } else {
    $scope.departureTime = moment().add(3, 'hours').minute(0).second(0);
  }

  // Watch the values and update them when changed
  $scope.$watch('arrivalTime', function() {
    $scope.getArrivalTime = moment($scope.arrivalTime).calendar();
  })

  $scope.$watch('departureTime', function() {
    $scope.getDepartureTime = moment($scope.departureTime).calendar();
  })

  $ionicPlatform.ready(function() {
    // Datepicker
    $scope.setArrivalTime = function() {
      $cordovaDatePicker.show({
        date: $scope.arrivalTime,
        mode: 'datetime',
        minDate: Date,
        maxDate: moment().add(1, 'day').endOf('day'),
        allowOldDates: false,
        minuteInterval: 30
      }).then(function(datetime) {
        $scope.arrivalTime = moment(datetime);
      });
    }

    $scope.setDepartureTime = function() {
      $cordovaDatePicker.show({
        date: $scope.departureTime,
        mode: 'datetime',
        minDate: Date,
        maxDate: moment().add(1, 'day').endOf('day'),
        allowOldDates: false,
        minuteInterval: 30
      }).then(function(datetime) {
        $scope.departureTime = moment(datetime);
      });
    }
  });

  $scope.activatedArrival = false;
  $scope.activatedDeparture = false;

  $scope.acceptRequest = function(index) {
  }
  
  $scope.declineRequest = function(index) {
    $scope.requests.splice(index, 1);
  }

  $scope.toggleRequest = function(direction) {
    var endpoint, data = {};
    data.netID = $scope.user.netID;
    data.direction = direction;

    if (direction === 0) {
      if (!$scope.activatedArrival) {
        endpoint = '/api/addRequest';
        data.time = $scope.arrivalTime.unix();
      } else {
        endpoint = '/api/removeRequest';
      }

      $scope.activatedArrival = !$scope.activatedArrival;
    } else {
      if (!$scope.activatedDeparture) {
        endpoint = '/api/addRequest';
        data.time = $scope.arrivalTime.unix();
      } else {
        endpoint = '/api/removeRequest';
      }

      $scope.activatedDeparture = !$scope.activatedDeparture;
    }

    $http({
      method: 'POST',
      url: API_URL + endpoint,
      data: data,
      headers: {'Content-Type': 'application/json'}
    }).then(function successCallback(response) {
      console.log(response);
    }, function errorCallback(response) {
      console.log(response);

      if (direction === 0) {
        $scope.activatedArrival = !$scope.activatedArrival;
      } else {
        $scope.activatedDeparture = !$scope.activatedDeparture;
      }

      $scope.showRequestFailedAlert = function() {
        var alertPopup = $ionicPopup.alert({
          title: 'Request failed!',
          template: 'Something went wrong.'
        });
      };

      $scope.showRequestFailedAlert();
    });
  }
})



.controller('RegistrationCtrl', function($scope, $stateParams, $http) {
  $scope.registrationData = {};

  $scope.registerAccount = function() {
    
  }
})

.controller('UploadCtrl', function($scope, $stateParams, $rootScope, $ionicHistory) {
  if (document.getElementById('DropzoneElementId')) {
    var myDropzone = new Dropzone("div#ical-dropzone", { url: "/file/post"});
  }

  $scope.goHome = function(){
    $ionicHistory.goBack(-2);
  }
  
  $scope.uploadSchedule = function() {
    $scope.goHome();
  }
})

.controller('ListingCtrl', function($scope, $stateParams, $rootScope, $http, $ionicModal) {

});