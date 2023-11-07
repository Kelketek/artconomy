// Stupid plugin which exists because the test framework can't handle modals for whatever reason.
//
// For floating items, we specify the 'attach' property and depending on which way this plugin is configured it will be
// undefined or else it will be the name of a div that's only really needed in a test environment.

import {createApp} from 'vue'

export const createTargetsPlugin = (testMode: boolean) => {
  const plugin =  {
    computed: {
      $modalTarget() {
        return testMode ? '#modal-target' : false
      },
      $snackbarTarget() {
        return testMode ? '#snackbar-target' : false
      },
      $statusTarget() {
        return testMode ? '#status-target' : false
      },
      $menuTarget() {
        return testMode ? '#menu-target' : false
      }
    }
  }
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(plugin)
    }
  }
}
