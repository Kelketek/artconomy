<template>
  <v-container fluid class="pa-0">
    <v-img :src="banner" :aspect-ratio="16/9" max-height="250px" :eager="prerendering">
      <v-row no-gutters
             align="center"
             justify="center"
             class="hero-text fill-height"
      >
        <v-col class="text-center">
          <h1 class="display-2 font-weight-thin mb-3">Always Open</h1>
          <h2>24/7 Commissions</h2>
        </v-col>
      </v-row>
    </v-img>
    <v-container>
      <v-row no-gutters class="py-2">
        <v-col class="text-center d-flex" cols="12" md="4">
          <v-row no-gutters>
            <v-col class="grow pa-1">
              <v-row no-gutters>
                <v-col cols="6" md="12" order="2" order-md="1">
                  <v-img :src="laptop" max-height="20vh" contain :eager="prerendering"/>
                </v-col>
                <v-col cols="6" md="12" order="1" order-md="2">
                  <v-row no-gutters class="justify-content fill-height" align="center">
                    <v-col class="pa-1">
                      Find an artist <strong>TODAY</strong>. No more hunting through journals and tweets!
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
            <v-col class="hidden-sm-and-down shrink">
              <v-divider vertical/>
            </v-col>
          </v-row>
        </v-col>
        <v-col class="text-center d-flex" cols="12" md="4">
          <v-row no-gutters>
            <v-col class="grow pa-1">
              <v-row no-gutters>
                <v-col cols="6" md="12">
                  <v-img :src="fingerPainting" max-height="20vh" contain :eager="prerendering"/>
                </v-col>
                <v-col class="pa-1" cols="6" md="12">
                  <v-row no-gutters class="justify-content fill-height" align="center">
                    <v-col>
                      <p>Get updates on your commission's progress, with revisions and direct messages.</p>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
            <v-col class="hidden-sm-and-down shrink">
              <v-divider vertical/>
            </v-col>
          </v-row>
        </v-col>
        <v-col class="text-center d-flex" cols="12" md="4">
          <v-row no-gutters>
            <v-col class="grow pa-1">
              <v-row no-gutters>
                <v-col cols="6" md="12" order="2" order-md="1">
                  <v-img :src="fridge" max-height="20vh" contain :eager="prerendering"/>
                </v-col>
                <v-col class="pa-1" cols="6" md="12" order="1" order-md="2">
                  <v-row no-gutters class="justify-content fill-height" align="center">
                    <v-col>
                      Show off your commissions-- make a profile and gallery for your characters!
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col class="text-center" cols="12">
          <v-btn large color="green" @click="search" :block="display.xs.value" variant="flat" class="commission-cta">
            <v-icon left :icon="mdiPalette"/>
            Commission an Artist Now!
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<style scoped>
.hero-text {
  text-shadow: 2px 2px 5px #000000;
}
</style>

<script setup lang="ts">
import {BASE_URL} from '@/lib/lib.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useRouter} from 'vue-router'
import {usePrerendering} from '@/mixins/prerendering.ts'
import {mdiPalette} from '@mdi/js'
import {useDisplay} from 'vuetify'

const router = useRouter()
const display = useDisplay()

const fridge = new URL('/static/images/fridge.png', BASE_URL).href
const fingerPainting = new URL('/static/images/fingerpainting.png', BASE_URL).href
const laptop = new URL('/static/images/laptop.png', BASE_URL).href
const banner = new URL('/static/images/banner.jpg', BASE_URL).href

const search = () => {
  searchForm.reset()
  router.push({
    name: 'SearchProducts',
    query: searchForm.rawData,
  })
}

const searchForm = useForm('search')

const {prerendering} = usePrerendering()
</script>
