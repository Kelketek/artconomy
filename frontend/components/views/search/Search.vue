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
                  <v-icon left :icon="mdiBasket"/>
                  Products
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn :to="{name: 'SearchSubmissions', query: $route.query}" density="comfortable" block class="rounded-0" variant="flat">
                  <v-icon left :icon="mdiImage"/>
                  Submissions
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn :to="{name: 'SearchCharacters', query: $route.query}" density="comfortable" block class="rounded-0" variant="flat">
                  <v-icon left :icon="mdiAccount"/>
                  Characters
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn :to="{name: 'SearchProfiles', query: $route.query}" density="comfortable" block class="rounded-0" variant="flat">
                  <v-icon left :icon="mdiAccountCircle"/>
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

<script setup lang="ts">
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {listenForList} from '@/store/lists/hooks.ts'
import {useRoute, useRouter} from 'vue-router'
import {mdiAccount, mdiAccountCircle, mdiBasket, mdiImage} from '@mdi/js'

const searchForm = useForm('search')
listenForList('searchProducts')
listenForList('searchSubmissions')
listenForList('searchCharacters')
listenForList('searchProfiles')
const route = useRoute()
const router = useRouter()
if (route.name === 'Search') {
  router.replace({
    name: 'SearchProducts',
    params: {...route.params},
    query: {...route.query},
  })
}
</script>
