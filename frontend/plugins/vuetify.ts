/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Composables
import DateFnsAdapter from "@date-io/date-fns"
import { createVuetify as upstreamCreateVuetify } from "vuetify"
import { aliases, mdi } from "vuetify/iconsets/mdi-svg"
import colors from "vuetify/util/colors"

const adapter = new DateFnsAdapter()

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides

export const createVuetify = () => {
  return upstreamCreateVuetify({
    date: {
      adapter,
    },
    icons: {
      defaultSet: "mdi",
      aliases,
      sets: {
        mdi,
      },
    },
    theme: {
      defaultTheme: "dark",
      variations: {
        colors: ["primary", "secondary", "well"],
        lighten: 4,
        darken: 4,
      },
      themes: {
        dark: {
          dark: true,
          colors: {
            primary: colors.blue.darken2,
            secondary: colors.purple.base,
            danger: colors.red.base,
            well: colors.grey.base,
          },
        },
      },
    },
  })
}
