<template>
  <v-row no-gutters>
    <v-col cols="12" class="text-center">
      <v-expansion-panels v-model="panel">
        <v-expansion-panel>
          <v-expansion-panel-header class="pa-1">
            <v-row no-gutters>
              <v-col class="text-center extra-height">
                <v-icon left>settings</v-icon>Search Options
                <v-chip v-if="searchForm.fields.shield_only.value" color="green" class="mx-1">shield</v-chip>
                <v-chip v-if="searchForm.fields.watch_list.value" color="primary" class="mx-1">watchlist</v-chip>
                <v-chip v-if="searchForm.fields.featured.value" color="secondary" class="mx-1">featured</v-chip>
                <v-chip v-if="searchForm.fields.rating.value" color="yellow" class="mx-1" light>high rated</v-chip>
                <v-chip v-if="searchForm.fields.max_price.value" color="red" class="mx-1">max price</v-chip>
                <v-chip v-if="searchForm.fields.min_price.value" color="black" class="mx-1">min price</v-chip>
              </v-col>
            </v-row>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-card-text>
              <v-row no-gutters  >
                <v-col cols="12" sm="6" md="4" v-if="isRegistered">
                  <ac-bound-field
                    :field="searchForm.fields.watch_list"
                    field-type="v-checkbox"
                    label="Watch List"
                    :persistent-hint="true"
                    hint="Only return results from artists on my watch list."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.shield_only"
                    field-type="v-checkbox"
                    label="Shield Only"
                    :persistent-hint="true"
                    hint="Only show products guaranteed by Artconomy Shield."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.featured"
                    field-type="v-checkbox"
                    label="Featured"
                    :persistent-hint="true"
                    hint="Only show featured products curated by Artconomy.com's staff."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.rating"
                    field-type="v-checkbox"
                    label="Best Reviewed First"
                    :persistent-hint="true"
                    hint="Sort from highest reviewed product to lowest."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.max_price"
                    label="Max Price"
                    :persistent-hint="true"
                    hint="Only show products with a price equal to or lower than this amount."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.min_price"
                    label="Min Price"
                    :persistent-hint="true"
                    hint="Only show products with a price equal to or higher than this amount."
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-col>
  </v-row>
</template>

<style scoped>
  .extra-height {
    line-height: 2.5;
  }
</style>

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
}
</script>
