<template>
  <v-col>
    <v-row no-gutters>
      <v-col class="text-center" cols="12">
        Try terms like:
        <p>
          <v-chip
            color="secondary"
            variant="flat"
            class="mx-1"
            @click="search('fox')"
          >
            fox
          </v-chip>
          <v-chip
            color="secondary"
            variant="flat"
            class="mx-1"
            @click="search('pony')"
          >
            pony
          </v-chip>
          <v-chip
            color="secondary"
            variant="flat"
            class="mx-1"
            @click="search('chibi')"
          >
            chibi
          </v-chip>
          <v-chip
            color="secondary"
            variant="flat"
            class="mx-1"
            @click="search('refsheet')"
          >
            refsheet
          </v-chip>
        </p>
      </v-col>
    </v-row>
  </v-col>
</template>

<script setup lang="ts">
import { useForm } from "@/store/forms/hooks.ts"

const searchForm = useForm("search")
const search = (val: string) => (searchForm.fields.q.model = val)
</script>
