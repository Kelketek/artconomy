<template>
  <v-flex xs12 text-xs-center class="pt-2">
    <v-expansion-panel v-model="panel">
      <v-expansion-panel-content>
        <span slot="header"><v-icon left>settings</v-icon>Search Options</span>
        <v-card-text>
          <v-layout row wrap>
            <v-flex xs12 sm6 md4 v-if="isRegistered">
              <ac-bound-field
                  :field="searchForm.fields.watch_list"
                  field-type="v-checkbox"
                  label="Watch List"
                  :persistent-hint="true"
                  hint="Only return results from artists on my watch list."
              />
            </v-flex>
            <v-flex xs12 sm6 md4>
              <ac-bound-field
                  :field="searchForm.fields.shield_only"
                  field-type="v-checkbox"
                  label="Shield Only"
                  :persistent-hint="true"
                  hint="Only show products guaranteed by Artconomy Shield."
              />
            </v-flex>
            <v-flex xs12 sm6 md4>
              <ac-bound-field
                  :field="searchForm.fields.featured"
                  field-type="v-checkbox"
                  label="Featured"
                  :persistent-hint="true"
                  hint="Only show featured products curated by Artconomy.com's staff."
              />
            </v-flex>
            <v-flex xs12 sm6 md4>
              <ac-bound-field
                  :field="searchForm.fields.rating"
                  field-type="v-checkbox"
                  label="Best Reviewed First"
                  :persistent-hint="true"
                  hint="Sort from highest reviewed product to lowest."
              />
            </v-flex>
            <v-flex xs12 sm6 md4>
              <ac-bound-field
                  :field="searchForm.fields.max_price"
                  label="Max Price"
                  :persistent-hint="true"
                  hint="Only show products with a price equal to or lower than this amount."
              />
            </v-flex>
            <v-flex xs12 sm6 md4>
              <ac-bound-field
                  :field="searchForm.fields.min_price"
                  label="Min Price"
                  :persistent-hint="true"
                  hint="Only show products with a price equal to or higher than this amount."
              />
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-flex>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import SearchHints from '../mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
  @Component({
    components: {AcBoundField},
  })
export default class ProductExtra extends mixins(SearchHints, Viewer) {
    public panel: null|number = null
    public created() {
      const keys = Object.keys(this.searchForm.rawData).filter((key) => key !== 'q')
      if (keys.length) {
        // Expansion panel is zero indexed, so this will expand the panel. Null is none expanded.
        this.panel = 0
      }
    }
}
</script>
