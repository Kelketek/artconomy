<template>
  <v-container>
    <v-layout row wrap>
      <v-flex xs12 sm6 md3 lg4 order-xs1 order-sm1>
        <ac-bound-field :field="searchForm.fields.q" label="I'm looking for..." :autofocus="true"></ac-bound-field>
      </v-flex>
      <v-flex xs12 sm6 md5 lg4 xl3 order-xs3 order-sm2>
        <router-view name="hints"></router-view>
      </v-flex>
      <v-flex xs12 md4 xl5 text-xs-center order-xs2 order-sm3>
        <v-layout column>
          <v-flex shrink>
            <h2>Search in...</h2>
          </v-flex>
          <v-flex grow>
            <v-btn-toggle>
              <v-btn :to="{name: 'SearchProducts', query: $route.query}">
                <v-icon left>shopping_basket</v-icon>
                Products
              </v-btn>
              <v-btn :to="{name: 'SearchSubmissions', query: $route.query}">
                <v-icon left>image</v-icon>
                Submissions
              </v-btn>
            </v-btn-toggle>
            <v-btn-toggle>
              <v-btn :to="{name: 'SearchCharacters', query: $route.query}">
                <v-icon left>people</v-icon>
                Characters
              </v-btn>
              <v-btn :to="{name: 'SearchProfiles', query: $route.query}">
                <v-icon left>account_circle</v-icon>
                Profiles
              </v-btn>
            </v-btn-toggle>
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
    <router-view name="extra"></router-view>
    <router-view class="pt-3"></router-view>
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
