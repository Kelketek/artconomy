<template>
  <v-container v-if="searchForm">
    <v-row no-gutters>
      <v-col cols="12" sm="6" md="3" lg="4" order="1" order-sm="1">
        <ac-bound-field :field="searchForm.fields.q" label="I'm looking for..." :autofocus="true"/>
      </v-col>
      <v-col cols="12" sm="6" md="5" lg="4" xl="3" order="3" order-sm="2">
        <router-view name="hints"/>
      </v-col>
      <v-col class="text-center" cols="12" md="4" xl="5" order="2" order-sm="3">
        <v-col>
          <v-col class="shrink">
            <h2>Search in...</h2>
          </v-col>
          <v-col class="grow">
            <v-row no-gutters>
              <v-col cols="6">
                <v-btn :to="{name: 'SearchProducts', query: $route.query}" density="comfortable" block class="rounded-0" variant="flat">
                  <v-icon left icon="mdi-basket"/>
                  Products
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn :to="{name: 'SearchSubmissions', query: $route.query}" density="comfortable" block class="rounded-0" variant="flat">
                  <v-icon left icon="mdi-image"/>
                  Submissions
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn :to="{name: 'SearchCharacters', query: $route.query}" density="comfortable" block class="rounded-0" variant="flat">
                  <v-icon left icon="mdi-account"/>
                  Characters
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn :to="{name: 'SearchProfiles', query: $route.query}" density="comfortable" block class="rounded-0" variant="flat">
                  <v-icon left icon="mdi-account-circle"/>
                  Profiles
                </v-btn>
              </v-col>
            </v-row>
          </v-col>
        </v-col>
      </v-col>
    </v-row>
    <router-view name="extra"/>
    <router-view class="pt-3"/>
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'

@Component({
  components: {AcBoundField},
})
class Search extends mixins(Viewer) {
  public searchForm: FormController = null as unknown as FormController

  public created() {
    this.searchForm = this.$getForm('search')
    this.$listenForList('searchProducts')
    this.$listenForList('searchSubmissions')
    this.$listenForList('searchCharacters')
    this.$listenForList('searchProfiles')
    if (this.$route.name === 'Search') {
      this.$router.replace({
        name: 'SearchProducts',
        params: {...this.$route.params},
        query: {...this.$route.query},
      })
    }
  }
}

export default toNative(Search)
</script>
