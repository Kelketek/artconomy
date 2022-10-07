<template>
  <v-container v-if="searchForm">
    <v-row no-gutters  >
      <v-col cols="12" sm="6" md="3" lg="4" order="1" order-sm="1">
        <ac-bound-field :field="searchForm.fields.q" label="I'm looking for..." :autofocus="true" />
      </v-col>
      <v-col cols="12" sm="6" md="5" lg="4" xl="3" order="3" order-sm="2">
        <router-view name="hints" />
      </v-col>
      <v-col class="text-center" cols="12" md="4" xl="5" order="2" order-sm="3">
        <v-col>
          <v-col class="shrink" >
            <h2>Search in...</h2>
          </v-col>
          <v-col class="grow">
            <v-btn-toggle dense>
              <v-btn :to="{name: 'SearchProducts', query: $route.query}">
                <v-icon left>shopping_basket</v-icon>
                Products
              </v-btn>
              <v-btn :to="{name: 'SearchSubmissions', query: $route.query}">
                <v-icon left>image</v-icon>
                Submissions
              </v-btn>
            </v-btn-toggle>
            <v-btn-toggle dense>
              <v-btn :to="{name: 'SearchCharacters', query: $route.query}">
                <v-icon left>people</v-icon>
                Characters
              </v-btn>
              <v-btn :to="{name: 'SearchProfiles', query: $route.query}">
                <v-icon left>account_circle</v-icon>
                Profiles
              </v-btn>
            </v-btn-toggle>
          </v-col>
        </v-col>
      </v-col>
    </v-row>
    <router-view name="extra" />
    <router-view class="pt-3" />
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
  @Component({
    components: {AcBoundField},
  })
export default class Search extends mixins(Viewer) {
    public searchForm: FormController = null as unknown as FormController

    public created() {
      this.searchForm = this.$getForm('search')
      this.$listenForList('searchProducts')
      this.$listenForList('searchSubmissions')
      this.$listenForList('searchCharacters')
      this.$listenForList('searchProfiles')
      if (this.$route.name === 'Search') {
        this.$router.replace({name: 'SearchProducts', params: {...this.$route.params}, query: {...this.$route.query}})
      }
    }
}
</script>
