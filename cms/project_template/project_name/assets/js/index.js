import Vue from "vue";

import Action from "./components/Action/Action.js";

const app = {
  components: {
    "action": Action
  }
};

new Vue(app).$mount("body");
