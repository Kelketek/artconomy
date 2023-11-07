<template>
  <v-container fluid class="pa-0">
    <v-img :src="banner" :aspect-ratio="16/9" max-height="250px">
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
                  <v-img :src="laptop" max-height="20vh" contain/>
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
                  <v-img :src="fingerPainting" max-height="20vh" contain/>
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
                  <v-img :src="fridge" max-height="20vh" contain/>
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
          <v-btn large color="green" @click="search" :block="$vuetify.display.xs" variant="flat" class="commission-cta">
            <v-icon left icon="mdi-palette"/>
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

<script lang="ts">
import {Component, toNative, Vue} from 'vue-facing-decorator'
import {FormController} from '@/store/forms/form-controller'
import {ArtVue, BASE_URL} from '@/lib/lib'

@Component
class AlwaysOpen extends ArtVue {
  public searchForm: FormController = null as unknown as FormController
  public fridge = new URL('/static/images/fridge.png', BASE_URL).href
  public fingerPainting = new URL('/static/images/fingerpainting.png', BASE_URL).href
  public laptop = new URL('/static/images/laptop.png', BASE_URL).href
  public banner = new URL('/static/images/banner.jpg', BASE_URL).href

  public search() {
    this.searchForm.reset()
    this.$router.push({
      name: 'SearchProducts',
      query: this.searchForm.rawData,
    })
  }

  public created() {
    this.searchForm = this.$getForm('search')
  }
}

export default toNative(AlwaysOpen)
</script>
