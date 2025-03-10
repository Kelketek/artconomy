<template>
  <v-container
    class="pa-0"
    fluid
  >
    <v-row no-gutters>
      <v-col
        class="shrink text-center"
        cols="12"
      >
        <v-pagination
          v-if="list.totalPages > 1 && showPagination"
          v-model="list.currentPage"
          :length="list.totalPages"
          :class="{prerendering}"
          v-bind="extraParams"
        />
      </v-col>
      <v-col cols="12">
        <ac-load-section
          :controller="list"
          class="load-section"
          :force-render="list.grow && !!list.list.length"
          :load-on-grow="false"
        >
          <template #default>
            <v-row
              v-if="list.list.length"
              no-gutters
            >
              <slot>
                <v-col
                  v-for="item in list.list"
                  :key="item.x!.id"
                >
                  {{ item.x }}
                </v-col>
              </slot>
            </v-row>
            <v-row
              v-else
              no-gutters
            >
              <slot name="empty">
                <v-col class="text-center">
                  Nothing to see here.
                </v-col>
              </slot>
            </v-row>
          </template>
          <template #failure>
            <slot name="failure" />
          </template>
          <template #empty>
            <slot name="empty" />
          </template>
        </ac-load-section>
      </v-col>
      <v-col
        v-if="list.grow"
        class="text-center"
        cols="12"
      >
        <ac-grow-spinner :list="list" />
      </v-col>
      <v-col
        class="shrink text-center"
        cols="12"
      >
        <v-pagination
          v-if="list.totalPages > 1 && showPagination"
          v-model="list.currentPage"
          :length="list.totalPages"
          :class="{prerendering}"
          v-bind="extraParams"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {ListController} from '@/store/lists/controller.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import AcGrowSpinner from '@/components/AcGrowSpinner.vue'
import {usePrerendering} from '@/mixins/prerendering.ts'
import {computed, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'

declare interface AcPaginatedProps {
  autoRun?: boolean,
  trackPages?: boolean,
  pageVariable?: string,
  list: ListController<any>,
  okStatuses?: number[],
  showPagination?: boolean,
}
const props = withDefaults(
    defineProps<AcPaginatedProps>(),
    {
      autoRun: true,
      trackPages: false,
      pageVariable: 'page',
      okStatuses: () => [],
      showPagination: true,
    },
)
const {prerendering} = usePrerendering()
const route = useRoute()
const router = useRouter()
const {statusOk} = useErrorHandling()

const extraParams = computed(() => {
  /* istanbul ignore if */
  if (prerendering.value) {
    return {'total-visible': 5}
  }
  return undefined
})

const list = props.list

watch(() => list.currentPage, (val) => {
  // istanbul ignore if
  if (!val) {
    return
  }
  if (!props.trackPages) {
    return
  }
  const query = {...route.query}
  query[props.pageVariable] = val + ''
  router.replace({query})
})

if (props.trackPages) {
  if (route.query[props.pageVariable]) {
    list.currentPage = parseInt(route.query[props.pageVariable] + '', 10)
  }
}
if (props.autoRun) {
  list.firstRun().catch(statusOk(...props.okStatuses))
}
</script>

<style>
.v-pagination.prerendering .v-pagination__item {
  display: none;
}
</style>
